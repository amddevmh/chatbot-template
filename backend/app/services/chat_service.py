"""
Chat service with session memory using LangGraph, aligned with official docs 
"""
import json
import logging
import threading
import traceback
import uuid
from datetime import datetime
from typing import Optional, Tuple, List

from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from functools import wraps

# Handle different import paths based on environment
try:
    from langgraph.checkpoint.mongodb import MongoDBSaver
    from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
except ImportError:
    try:
        from langgraph_checkpoint_mongodb import MongoDBSaver
        from langgraph_checkpoint_mongodb.aio import AsyncMongoDBSaver
    except ImportError:
        logging.error("Could not import MongoDB checkpoint functionality. "
                     "Make sure either langgraph with MongoDB support or "
                     "langgraph-checkpoint-mongodb is installed.")
        raise

from app.config import settings
from app.database.mongodb import client as mongo_client, DATABASE_NAME
from app.models.chat_session import ChatSessionMetadata
from app.services.chat_workflow import build_chat_graph  # Import the graph builder

# Set higher logging level for noisy libraries
logging.getLogger('pymongo').setLevel(logging.WARNING)
logging.getLogger('passlib').setLevel(logging.WARNING)
logging.getLogger('jwt').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Track active sessions for concurrent request analysis
active_sessions = {}
active_sessions_lock = threading.Lock()

# Define a reusable retry decorator for database operations
def with_database_retry(operation_name=None):
    def decorator(func):
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=4, max=10),
            retry=retry_if_exception_type(Exception),
            before=lambda retry_state: logger.debug(
                f"Attempt {retry_state.attempt_number} for {operation_name or func.__name__}"
            ),
            after=lambda retry_state: logger.debug(
                f"Completed {operation_name or func.__name__} after {retry_state.attempt_number} attempts"
            )
        )
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {operation_name or func.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator



class ChatService:
    """Service for stateful chat interactions with an LLM using LangGraph memory and non linear flows"""

    """__init__ sets up the foundation but doesn't fully initialize Memory, which requires an async context. Check #Memory section for full initialization."""

    def __init__(self):
        # Initialize logging
        logger.info("Initializing ChatService")

        # Placeholder for async-initialized memory
        self.memory = None
        self._memory_initialized = False

        # MongoDB client and DB params for memory checkpoints
        self._memory_params = {
            "client": mongo_client,
            "db_name": DATABASE_NAME,
            "collection_name": settings.MONGODB_CHECKPOINT_COLLECTION
        }

        # Initialize the LLM
        try:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.7,
                max_tokens=500,
            )
            logger.info(f"Initialized ChatOpenAI with model: {settings.LLM_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatOpenAI: {str(e)}")
            logger.error(traceback.format_exc())
            raise

        # Build the graph with temporary synchronous memory saver
        temp_memory = MongoDBSaver(
            client=self._memory_params["client"],
            db_name=self._memory_params["db_name"],
            collection_name=self._memory_params["collection_name"]
        )
        self.graph = build_chat_graph(self.llm, temp_memory)
        logger.info("ChatService initialized with temporary memory saver")
    

        
    # Memory Management
    async def initialize_async_memory(self):
        """Initialize the AsyncMongoDBSaver in an async context."""
        if hasattr(self, "_memory_initialized") and self._memory_initialized:
            logger.debug("AsyncMongoDBSaver already initialized")
            return
        try:
            logger.info("Initializing AsyncMongoDBSaver in async context")
            self.memory = AsyncMongoDBSaver(
                client=self._memory_params["client"],
                db_name=self._memory_params["db_name"],
                collection_name=self._memory_params["collection_name"]
            )
            self._memory_initialized = True
            logger.info("AsyncMongoDBSaver initialized successfully")
            # Rebuild the graph with the async memory saver
            self.graph = build_chat_graph(self.llm, self.memory)
            logger.info("Graph rebuilt with AsyncMongoDBSaver")
        except Exception as e:
            logger.error(f"Error initializing AsyncMongoDBSaver: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    async def get_chat_response(self, message: str, session_id: str) -> str | Tuple[str, Optional[str]]:
        """
        Process a chat message and return the response.

        Args:
            message: The user's input message.
            session_id: Unique identifier for the chat session.

        Returns:
            str: The assistant's response.
        """
        if not self._memory_initialized:
            await self.initialize_async_memory()

        config = {"configurable": {"thread_id": session_id}}
        input_state = {"messages": [{"role": "user", "content": message}]}

        try:
            with active_sessions_lock:
                active_sessions[session_id] = active_sessions.get(session_id, 0) + 1
            logger.debug(f"Active sessions: {len(active_sessions)}")

            output = await self.graph.ainvoke(input_state, config)
            checkpoint = await self.graph.aget_state(config)
            response = checkpoint.values["messages"][-1].content

            logger.info(f"Generated response for session {session_id}: {response[:100]}...")
            return response

        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            logger.error(traceback.format_exc())
            return "I'm sorry, I encountered an error processing your request."
        finally:
            with active_sessions_lock:
                active_sessions[session_id] -= 1
                if active_sessions[session_id] <= 0:
                    del active_sessions[session_id]
            logger.debug(f"Active sessions after cleanup: {len(active_sessions)}")

    ## Sessions Mgmnt
    @with_database_retry(operation_name="generate_session_id")
    async def generate_session_id(self, username: str, custom_id: str = None) -> str:
        """Generate a session ID using username and optional custom ID
        
        This ensures that session IDs are unique and associated with a specific user.
        
        Args:
            username: The username of the user
            custom_id: Optional custom identifier for the session
            
        Returns:
            A unique session ID string
        """
        if custom_id:
            return f"{username}_{custom_id}"
        else:
            print(f"Generating session ID for user: {username}")
            # Generate a unique ID if none provided
            unique_id = str(uuid.uuid4())[:8]
            return f"{username}_{unique_id}"
    
    @with_database_retry(operation_name="create_session")
    async def create_session(self, username: str, session_name: str = "New Chat") -> dict:
        """Create a new chat session and store metadata
        
        Args:
            username: The username of the user
            session_name: Optional name for the session
            
        Returns:
            Session metadata dictionary
        """
        session_id = await self.generate_session_id(username)
        
        # Create session metadata document
        session = ChatSessionMetadata(
            session_id=session_id,
            username=username,
            name=session_name,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            message_count=0
        )
        
        # Insert the session document
        await session.insert()
        logger.info(f"Created new session {session_id} for user {username}")
        persisted = True
        
        # Return session data with persistence status
        return {
            "session_id": session.session_id,
            "name": session.name,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": session.message_count,
            "persisted": persisted
        }
    
    @with_database_retry(operation_name="list_user_sessions")
    async def list_user_sessions(self, username: str) -> List[dict]:
        """List all sessions for a user
        
        Args:
            username: The username of the user
            
        Returns:
            List of session metadata dictionaries
        """
        # Find all sessions for this user, sorted by updated_at (newest first)
        sessions = await ChatSessionMetadata.find(
            ChatSessionMetadata.username == username
        ).sort([("updated_at", -1)]).to_list()
        
        # Convert to dictionaries
        return [
            {
                "session_id": session.session_id,
                "name": session.name,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": session.message_count
            }
            for session in sessions
        ]
    
    @with_database_retry(operation_name="get_session_history")
    async def get_session_history(self, session_id: str) -> List[dict]:
        """Get message history for a session
        
        Args:
            session_id: The ID of the session
            
        Returns:
            List of message dictionaries
        """
        # Ensure AsyncMongoDBSaver is initialized in async context
        if not hasattr(self, "_memory_initialized") or not self._memory_initialized:
            logger.info(f"Initializing AsyncMongoDBSaver before retrieving session history for {session_id}")
            await self.initialize_async_memory()
            
        # Configure thread_id for persistent memory
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            # Get the current state from memory
            checkpoint = await self.graph.aget_state(config)
            
            # Debug logging to understand the checkpoint structure
            logger.info(f"Checkpoint type: {type(checkpoint)}")
            
            # For MongoDB persistence, we need to directly query the database
            # since the checkpoint structure might not expose messages properly
            try:
                # Get the most recent chat history from the database directly
                # LangGraph doesn't expose collection_name as an attribute
                # Let's check what collections actually exist in the database
                db = self.memory.client[self.memory.db_name]
                collections = await db.list_collection_names()
                logger.debug(f"Available collections in database: {collections}")
                
                # Based on LangGraph implementation, we know it uses specific collection names
                collection = db['checkpoints_aio']
                
                # Query for the latest checkpoint with this session_id (LangGraph thread_id)
                result = await collection.find_one(
                    {"thread_id": session_id},  # LangGraph uses thread_id as the persistence key
                    sort=[("timestamp", -1)]  # Get the most recent one
                )
                
                if result and "state" in result and "values" in result["state"]:
                    state_values = result["state"]["values"]
                    if "messages" in state_values:
                        messages_data = state_values["messages"]
                        logger.info(f"Found {len(messages_data)} messages in MongoDB for session {session_id}")
                        
                        # Format messages for API response
                        messages = []
                        for msg in messages_data:
                            # Handle different message formats
                            if isinstance(msg, dict):
                                role = msg.get("role", "unknown")
                                content = msg.get("content", str(msg))
                            else:
                                role = msg.type if hasattr(msg, "type") else "unknown"
                                content = msg.content if hasattr(msg, "content") else str(msg)
                                
                            messages.append({
                                "role": role,
                                "content": content
                            })
                        
                        return messages
            except Exception as db_err:
                logger.error(f"Error querying MongoDB directly: {str(db_err)}")
                logger.error(traceback.format_exc())
            
            # Fallback to using the checkpoint if direct DB query failed
            if checkpoint and hasattr(checkpoint, 'values') and "messages" in checkpoint.values:
                messages_data = checkpoint.values["messages"]
                
                # Format messages for API response
                messages = []
                for msg in messages_data:
                    messages.append({
                        "role": msg.type if hasattr(msg, "type") else "unknown",
                        "content": msg.content if hasattr(msg, "content") else str(msg)
                    })
                
                return messages
                
            logger.info(f"No messages found for session {session_id}")
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving session history for {session_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
    
    @with_database_retry(operation_name="update_session_metadata")
    async def update_session_metadata(self, session_id: str, increment_messages: int = 1):
        """Update session metadata when a new message is sent
        
        Args:
            session_id: The ID of the session
            increment_messages: Number of messages to increment the count by
        """
        try:
            # Find and update the session
            session = await ChatSessionMetadata.find_one(ChatSessionMetadata.session_id == session_id)
            if session:
                session.updated_at = datetime.now()
                session.message_count += increment_messages
                

                await session.save()
                logger.debug(f"Updated session metadata for {session_id}")
            else:
                logger.warning(f"Session {session_id} not found for metadata update")
        except Exception as e:
            logger.error(f"Error updating session metadata for {session_id}: {str(e)}")
            logger.error(traceback.format_exc())
    
    @with_database_retry(operation_name="update_session")
    async def update_session(self, username: str, session_id: str, name: str = None) -> dict:
        """Update a chat session's metadata
        
        Args:
            username: The username of the user
            session_id: The ID of the session
            name: New name for the session
            
        Returns:
            Updated session metadata dictionary
        """
        try:
            # Find the session
            session = await ChatSessionMetadata.find_one(ChatSessionMetadata.session_id == session_id)
            if not session:
                logger.warning(f"Session {session_id} not found for update")
                raise ValueError(f"Session {session_id} not found")
                
            # Verify ownership
            if session.username != username:
                logger.warning(f"User {username} attempted to update session {session_id} owned by {session.username}")
                raise ValueError(f"Session {session_id} does not belong to user {username}")
            
            # Update fields
            if name is not None:
                session.name = name
                
            session.updated_at = datetime.now()
            await session.save()
            
            logger.info(f"Updated session {session_id} for user {username}")
            
            # Return updated session data
            return {
                "session_id": session.session_id,
                "name": session.name,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": session.message_count
            }
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    @with_database_retry(operation_name="generate_session_title")
    async def generate_session_title(self, session_id: str) -> str:
        """Generate a title for a chat session based on its content
        
        Args:
            session_id: The ID of the session
            
        Returns:
            A generated title string
        """
        try:
            # Get the session messages
            messages = await self.get_session_history(session_id)
            
            # Need at least two messages to generate a meaningful title
            if len(messages) < 2:
                logger.info(f"Not enough messages in session {session_id} to generate title")
                return "New Chat"
            
            # Extract the first few messages for context (limit to avoid token issues)
            context_messages = messages[:min(3, len(messages))]
            message_texts = [f"{msg['role']}: {msg['content']}" for msg in context_messages]
            context = "\n".join(message_texts)
            
            # Create a system prompt for title generation
            system_prompt = "Based on this conversation, generate an ultra short, descriptive title, max 3 words. Respond with ONLY the title, no quotes or explanations."
            
            # Use the LLM to generate a title
            title_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ]
            
            # Use the same LLM instance but with different parameters for title generation
            response = await self.llm.ainvoke(
                title_messages,
                temperature=0.7,
                max_tokens=10  # Keep titles short
            )
            
            # Extract and clean the title
            title = response.content.strip()
            # Remove quotes if present
            title = title.strip('"').strip("'").strip()
            
            # If empty or too long, use a fallback
            if not title or len(title) > 50:
                logger.warning(f"Generated invalid title for session {session_id}: {title}")
                return "Chat Session"
                
            logger.info(f"Generated title for session {session_id}: {title}")
            return title
            
        except Exception as e:
            logger.error(f"Error generating title for session {session_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return "Chat Session"  # Fallback title
    
   