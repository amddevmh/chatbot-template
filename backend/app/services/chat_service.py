#!/usr/bin/env python3
"""
Chat service with session memory using LangGraph, aligned with official docs (Part 3)
"""
import logging
import time
import traceback
import asyncio
import threading
from typing import Annotated, Dict, Any
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from app.config import settings

# Configure logging with more detailed format
logging.basicConfig(
    level=settings.LOG_LEVEL or logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set higher logging level for noisy libraries
logging.getLogger('pymongo').setLevel(logging.WARNING)
logging.getLogger('passlib').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Track active sessions for concurrent request analysis
active_sessions = {}
active_sessions_lock = threading.Lock()

# Define the state as per the docs
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

class ChatService:
    """Service for stateful chat interactions with an LLM using LangGraph memory"""
    
    def __init__(self):
        logger.info(f"Initializing ChatService (Thread ID: {threading.get_ident()})")
        try:
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
            
            # Initialize MemorySaver with diagnostics
            try:
                self.memory = MemorySaver()
                logger.info("MemorySaver initialized successfully")
            except Exception as mem_err:
                logger.error(f"Memory initialization error: {str(mem_err)}")
                logger.error(traceback.format_exc())
                raise
            
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
    
    def _build_graph(self):
        """Build the LangGraph workflow with memory, matching docs"""
        graph_builder = StateGraph(State)
        
        async def chatbot(state: State):
            # Track timing for LLM invocation
            thread_id = threading.get_ident()
            start_time = time.time()
            logger.debug(f"[Thread {thread_id}] Starting LLM invocation with {len(state['messages'])} messages")
            
            try:
                # Invoke LLM with timeout handling
                response = await self.llm.ainvoke(state["messages"])
                elapsed = time.time() - start_time
                logger.info(f"[Thread {thread_id}] LLM responded in {elapsed:.2f}s: {response.content[:100]}...")
                return {"messages": [response]}
            except asyncio.TimeoutError:
                logger.error(f"[Thread {thread_id}] LLM invocation timeout after {time.time() - start_time:.2f}s")
                raise
            except Exception as e:
                logger.error(f"[Thread {thread_id}] LLM error: {str(e)}")
                logger.error(traceback.format_exc())
                raise
        
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        
        logger.debug("Compiling graph with memory saver...")
        try:
            compiled_graph = graph_builder.compile(checkpointer=self.memory)
            logger.debug("Graph compilation successful")
            return compiled_graph
        except Exception as e:
            logger.error(f"Error compiling graph: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    async def get_chat_response(self, message: str, session_id: str) -> str:
        """Get a response from the LLM with session context"""
        request_id = f"{session_id}_{int(time.time()*1000)}"
        thread_id = threading.get_ident()
        start_time = time.time()
        
        # Track concurrent sessions
        with active_sessions_lock:
            prev_count = len(active_sessions)
            active_sessions[request_id] = {
                'session_id': session_id,
                'thread_id': thread_id,
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
                
            # Configure thread_id for persistent memory
            config = {"configurable": {"thread_id": session_id}}
            
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
            input_state = {"messages": [{"role": "user", "content": message}]}
            
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