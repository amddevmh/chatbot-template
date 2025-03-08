#!/usr/bin/env python3
"""
Chat service with session memory using LangGraph, aligned with official docs (Part 3)
"""
import logging
from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the state as per the docs
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

class ChatService:
    """Service for stateful chat interactions with an LLM using LangGraph memory"""
    
    def __init__(self):
        logger.info("Initializing ChatService")
        self.llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model=settings.LLM_MODEL)
        self.memory = MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow with memory, matching docs"""
        graph_builder = StateGraph(State)
        
        async def chatbot(state: State):
            logger.info(f"Full messages sent to LLM: {state['messages']}")
            response = await self.llm.ainvoke(state["messages"])
            logger.info(f"LLM response: {response.content}")
            return {"messages": [response]}
        
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        
        return graph_builder.compile(checkpointer=self.memory)
    
    async def get_chat_response(self, message: str, session_id: str) -> str:
        """Get a response from the LLM with session context"""
        config = {"configurable": {"thread_id": session_id}}
        
        # Log the current state from memory
        checkpoint = await self.graph.aget_state(config)
        logger.info(f"State retrieved from memory before processing: {checkpoint.values if checkpoint else 'None'}")
        
        # Input state with new user message
        input_state = {"messages": [{"role": "user", "content": message}]}
        logger.info(f"Input state with new message: {input_state}")
        
        # Invoke the graph to get the final state
        final_state = await self.graph.ainvoke(input_state, config)
        
        # Log the final state and verify memory
        logger.info(f"Updated state after processing: {final_state['messages']}")
        updated_checkpoint = await self.graph.aget_state(config)
        logger.info(f"State retrieved from memory after processing: {updated_checkpoint.values if updated_checkpoint else 'None'}")
        
        # Return the last message's content (the assistant's response)
        return final_state["messages"][-1].content