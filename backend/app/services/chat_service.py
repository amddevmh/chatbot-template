#!/usr/bin/env python3
"""
Chat service with session memory using LangGraph, aligned with official docs (Part 3)
"""
import logging
import time
import traceback
import asyncio
import threading
import uuid
import os
from datetime import datetime
from typing import Annotated, Dict, Any, List, Optional
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from functools import wraps
# Handle different import paths based on environment
try:
    # Try the original import path first (for local development)
    from langgraph.checkpoint.mongodb import MongoDBSaver
    from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
except ImportError:
    # Fall back to the alternative package structure (for CI environment)
    try:
        from langgraph_checkpoint_mongodb import MongoDBSaver
        from langgraph_checkpoint_mongodb.aio import AsyncMongoDBSaver
    except ImportError:
        # If both fail, provide a helpful error message
        logging.error("Could not import MongoDB checkpoint functionality. "
                     "Make sure either langgraph with MongoDB support or "
                     "langgraph-checkpoint-mongodb is installed.")
        raise
from app.config import settings
from app.database.mongodb import client as mongo_client, DATABASE_NAME
from app.models.chat_session import ChatSessionMetadata

# Set higher logging level for noisy libraries
logging.getLogger('pymongo').setLevel(logging.WARNING)
logging.getLogger('passlib').setLevel(logging.WARNING)
logging.getLogger('jwt').setLevel(logging.WARNING)  # Also reduce JWT logging noise

logger = logging.getLogger(__name__)

# Track active sessions for concurrent request analysis
active_sessions = {}
active_sessions_lock = threading.Lock()

# Define a reusable retry decorator for database operations
def with_database_retry(operation_name=None):
    """
    A decorator that applies retry logic to database operations.
    
    Args:
        operation_name: Optional name for the operation for better logging
        
    Returns:
        A decorator that can be applied to async functions
    """
    # Create the retry decorator with our standard configuration
    retry_decorator = retry(
        stop=stop_after_attempt(3),  # Stop after 3 attempts
        wait=wait_exponential(multiplier=0.5, min=0.5, max=2),  # Exponential backoff
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying {operation_name or 'database operation'} "
            f"(attempt {retry_state.attempt_number}/3): {retry_state.outcome.exception()}"
        )
    )
    
    # Return a function that will apply this decorator to an async function
    def decorator(func):
        @wraps(func)  # Preserve function metadata
        async def wrapper(*args, **kwargs):
            try:
                # Apply the retry decorator to the function
                return await retry_decorator(func)(*args, **kwargs)
            except RetryError as retry_err:
                # All retries failed
                original_exception = retry_err.last_attempt.exception()
                logger.error(f"Failed {operation_name or func.__name__} after multiple retries: {str(original_exception)}")
                # Re-raise the original exception
                raise original_exception
        return wrapper
    return decorator

# Define the state as per the docs
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

class ChatService:
    """Service for stateful chat interactions with an LLM using LangGraph memory"""
    
    """This phase sets up the foundation but doesn't fully initialize the MongoDB persistence, which requires an async context."""
    def __init__(self):
        logger.info(f"Initializing ChatService (Thread ID: {threading.get_ident()})")
        try:
            # 1. API Key Validation TODO Edit validation to be LLM agnostic
            if not settings.OPENAI_API_KEY:
                logger.error("OPENAI_API_KEY not found in settings")
                raise ValueError("OPENAI_API_KEY is required for ChatService initialization")
                
            logger.info(f"Using LLM model: {settings.LLM_MODEL}")
            # Increase timeout for better handling of concurrent requests
            self.llm = ChatOpenAI(
                api_key=settings.OPENAI_API_KEY, 
                model=settings.LLM_MODEL,
                request_timeout=60  # Increase timeout to handle concurrent requests
            )
            logger.info("LLM initialized successfully")
            
            # We'll initialize the AsyncMongoDBSaver in an async context later
            # For now, use a placeholder that will be replaced in initialize_async_memory
            self._memory_initialized = False
            # Store the parameters for later async initialization
            self._memory_params = {
                "client": mongo_client,
                "db_name": DATABASE_NAME,
                "collection_name": "chat_memory"
            }
            logger.info("Memory parameters prepared for async initialization")
            
            logger.info("Building graph...")
            self.graph = self._build_graph()
            logger.info("Graph built successfully")
        except Exception as e:
            logger.error(f"Error initializing ChatService: {str(e)}")
            logger.error(traceback.format_exc())
            # Make sure the error propagates to show the real issue
            raise
            
        # Initialize request metrics
        self.request_metrics = {}
        self.request_metrics_lock = threading.Lock()
    
    @with_database_retry(operation_name="initialize_async_memory")
    async def initialize_async_memory(self):
        """Initialize the AsyncMongoDBSaver in an async context"""
        if hasattr(self, "_memory_initialized") and self._memory_initialized:
            logger.debug("AsyncMongoDBSaver already initialized")
            return
        
        try:
            logger.info("Initializing AsyncMongoDBSaver in async context")
            # Now we're in an async context, so we can initialize AsyncMongoDBSaver
            self.memory = AsyncMongoDBSaver(
                client=self._memory_params["client"],
                db_name=self._memory_params["db_name"],
                collection_name=self._memory_params["collection_name"]
            )
            self._memory_initialized = True
            logger.info("AsyncMongoDBSaver initialized successfully")
            
            # Recompile the graph with the new memory saver
            logger.info("Recompiling graph with AsyncMongoDBSaver")
            self.graph = self._build_graph()
            logger.info("Graph recompiled successfully")
        except Exception as e:
            logger.error(f"Error initializing AsyncMongoDBSaver: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _build_graph(self):
        """Build the LangGraph workflow with memory, matching docs"""
        graph_builder = StateGraph(State)
        
        async def chatbot(state: State):
            # Track timing for LLM invocation
            python_thread_id = threading.get_ident()
            start_time = time.time()
            logger.debug(f"[Thread {python_thread_id}] Starting LLM invocation with {len(state['messages'])} messages")
            
            try:
                # Invoke LLM with timeout handling
                response = await self.llm.ainvoke(state["messages"])
                elapsed = time.time() - start_time
                logger.info(f"[Thread {python_thread_id}] LLM responded in {elapsed:.2f}s: {response.content[:100]}...")
                return {"messages": [response]}
            except asyncio.TimeoutError:
                logger.error(f"[Thread {python_thread_id}] LLM invocation timeout after {time.time() - start_time:.2f}s")
                raise
            except Exception as e:
                logger.error(f"[Thread {python_thread_id}] LLM error: {str(e)}")
                logger.error(traceback.format_exc())
                raise
        
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        
        logger.debug("Compiling graph with memory saver...")
        try:
            # If we're in the initial synchronous initialization, use a temporary memory
            # This will be replaced when initialize_async_memory is called
            if not hasattr(self, "_memory_initialized") or not self._memory_initialized:
                logger.info("Using temporary synchronous MongoDBSaver for initial graph compilation")
                temp_memory = MongoDBSaver(
                    client=self._memory_params["client"],
                    db_name=self._memory_params["db_name"],
                    collection_name=self._memory_params["collection_name"]
                )
                compiled_graph = graph_builder.compile(checkpointer=temp_memory)
            else:
                # Use the properly initialized AsyncMongoDBSaver
                compiled_graph = graph_builder.compile(checkpointer=self.memory)
                
            logger.debug("Graph compilation successful")
            return compiled_graph
        except Exception as e:
            logger.error(f"Error compiling graph: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
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
    
    async def get_chat_response(self, message: str, session_id: str) -> str:
        """Get a response from the LLM with session context"""
        request_id = f"{session_id}_{int(time.time()*1000)}"
        python_thread_id = threading.get_ident()
        start_time = time.time()
        
        # Ensure AsyncMongoDBSaver is initialized in async context
        if not hasattr(self, "_memory_initialized") or not self._memory_initialized:
            logger.info(f"[{request_id}] Initializing AsyncMongoDBSaver before processing request")
            await self.initialize_async_memory()
        
        # Track concurrent sessions
        with active_sessions_lock:
            prev_count = len(active_sessions)
            active_sessions[request_id] = {
                'session_id': session_id,
                'python_thread_id': python_thread_id,
                'start_time': start_time,
                'message': message[:50] + '...' if len(message) > 50 else message
            }
            logger.info(f"[{request_id}] Starting request. Now handling {len(active_sessions)} concurrent requests")
            if prev_count > 0:
                logger.info(f"[{request_id}] Other active sessions: {[s for s in active_sessions if s != request_id]}")
            
        try:
            # Validate inputs
            if not message or not isinstance(message, str):
                logger.error(f"[{request_id}] Invalid message format: {message}")
                raise ValueError(f"Invalid message format: {message}")
                
            if not session_id or not isinstance(session_id, str):
                logger.error(f"[{request_id}] Invalid session_id format: {session_id}")
                raise ValueError(f"Invalid session_id: {session_id}")
                
            logger.info(f"[{request_id}] Processing message of length {len(message)} for session {session_id}")
                
            # Configure session_id for LangGraph persistent memory
            config = {"configurable": {"thread_id": session_id}}  # LangGraph uses thread_id for persistence
            
            # Log performance for each stage
            memory_fetch_start = time.time()
            
            # Log the current state from memory
            try:
                checkpoint = await self.graph.aget_state(config)
                memory_fetch_time = time.time() - memory_fetch_start
                logger.info(f"[{request_id}] Memory fetch took {memory_fetch_time:.2f}s")
                logger.debug(f"[{request_id}] State retrieved: {checkpoint.values if checkpoint else 'None'}")
            except Exception as e:
                logger.warning(f"[{request_id}] Failed to retrieve state: {str(e)}. Continuing with empty state.")
                logger.warning(traceback.format_exc())
                checkpoint = None
            
            # Input state with new user message
            # If we have an existing checkpoint, we need to add to it, otherwise create a new state
            if checkpoint and "messages" in checkpoint.values:
                # Add the new message to existing messages
                input_state = {"messages": checkpoint.values["messages"] + [{"role": "user", "content": message}]}
                logger.debug(f"[{request_id}] Adding to existing state with {len(checkpoint.values['messages'])} messages")
            else:
                # Start with just the new message
                input_state = {"messages": [{"role": "user", "content": message}]}
                logger.debug(f"[{request_id}] Creating new state with user message")
            
            # Invoke the graph to get the final state
            graph_start = time.time()
            logger.info(f"[{request_id}] Starting graph invocation at {graph_start-start_time:.2f}s into request")
            
            try:
                final_state = await self.graph.ainvoke(input_state, config)
                graph_time = time.time() - graph_start
                logger.info(f"[{request_id}] Graph invocation took {graph_time:.2f}s")
            except asyncio.TimeoutError:
                elapsed = time.time() - graph_start
                logger.error(f"[{request_id}] Timeout during graph invocation after {elapsed:.2f}s")
                # Log all active sessions to help diagnose contention
                with active_sessions_lock:
                    logger.error(f"[{request_id}] Active sessions during timeout: {active_sessions}")
                raise TimeoutError(f"Graph invocation timed out after {elapsed:.2f}s")
            except Exception as e:
                elapsed = time.time() - graph_start
                logger.error(f"[{request_id}] Error during graph invocation after {elapsed:.2f}s: {str(e)}")
                logger.error(traceback.format_exc())
                raise
            
            # Log the final state and verify memory
            logger.debug(f"[{request_id}] Updated state: {final_state['messages']}")
            
            # Skip post-verification in concurrent scenarios to avoid bottlenecks
            # Return the last message's content (the assistant's response)
            response = final_state["messages"][-1].content
            
            # Update session metadata to track message count and last update time
            try:
                await self.update_session_metadata(session_id, increment_messages=2)  # 1 for user, 1 for assistant
                logger.debug(f"[{request_id}] Updated session metadata for {session_id}")
            except Exception as e:
                logger.warning(f"[{request_id}] Failed to update session metadata: {str(e)}")
            
            total_time = time.time() - start_time
            logger.info(f"[{request_id}] Total request processing time: {total_time:.2f}s")
            
            return response
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[{request_id}] Error in get_chat_response after {elapsed:.2f}s: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        finally:
            # Clean up active sessions tracking
            with active_sessions_lock:
                if request_id in active_sessions:
                    del active_sessions[request_id]
                    logger.info(f"[{request_id}] Completed. Now handling {len(active_sessions)} concurrent requests")