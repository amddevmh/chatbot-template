import logging
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

logger = logging.getLogger(__name__)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def build_chat_graph(llm, checkpointer):
    """
    Build a LangGraph workflow for a simple chat system with a single node.

    Args:
        llm: The language model instance (e.g., ChatOpenAI) to generate responses.
        checkpointer: The checkpointer (e.g., AsyncMongoDBSaver) to persist state across runs.

    Returns:
        Compiled StateGraph instance ready to process chat messages.
    """
    async def generate_response_node(state: ChatState) -> ChatState:
        """
        Generate an LLM response based on the full conversation history.

        Args:
            state: The current ChatState, containing the messages list (full history + new input).

        Returns:
            Updated state with the LLM's response.

        Note:
            - state["messages"] includes the full history because LangGraph merges the persisted
              state (from checkpointer) with the new input (from ainvoke's input_state).
            - The returned state overwrites messages with just the LLM response, but the checkpointer
              with add_messages will append this to the persisted history.
        """
        logger.debug("Generating LLM response")
        try:
            # Log the messages sent to the LLM (replacing send_user_input_node's logging)
            latest_message = state["messages"][-1].content if state["messages"] else "No input"
            logger.info(f"Received user input: {latest_message[:50]}...")
            
            response = await llm.ainvoke(state["messages"])
            logger.info(f"LLM response: {response.content[:100]}...")
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            raise

    # Initialize the LangGraph workflow with the defined state
    graph_builder = StateGraph(ChatState)

    # Add the single node to the graph
    graph_builder.add_node("generate_response", generate_response_node)

    # Define the flow of the graph (START goes directly to generate_response)
    graph_builder.add_edge(START, "generate_response")
    graph_builder.add_edge("generate_response", END)

    # Compile the graph with the checkpointer for state persistence
    return graph_builder.compile(checkpointer=checkpointer)