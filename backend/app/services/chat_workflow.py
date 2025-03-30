import logging
import time
from typing import Annotated, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

logger = logging.getLogger(__name__)

class EnhancedState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    intent: Optional[str] = None
    calculation_result: Optional[str] = None

def build_chat_graph(llm, checkpointer):
    """
    Build and return the LangGraph workflow for chat processing.

    Args:
        llm: The language model instance to use in the nodes.
        checkpointer: The checkpointer (memory saver) to use for state persistence.

    Returns:
        Compiled StateGraph instance.
    """
    async def identify_intent(state: EnhancedState) -> EnhancedState:
        latest_message = state["messages"][-1].content if state["messages"] else ""
        if not latest_message:
            logger.warning("Empty message received for intent classification")
            state["intent"] = "other"
            return state
        intent_categories = ["calculator", "other"]
        system_prompt = """You are an intent classification system. 
        Classify the user message into exactly one of the following categories:
        - calculator: Mathematical expressions or requests for calculations
        - other: Any other type of message
        
        Respond with ONLY the category name, nothing else."""
        try:
            classification_response = await llm.ainvoke(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": latest_message}
                ],
                temperature=0.1,
                max_tokens=10
            )
            intent = classification_response.content.strip().lower()
            if intent in intent_categories:
                logger.info(f"AI identified intent: {intent} for message: {latest_message[:50]}...")
                state["intent"] = intent
            else:
                logger.warning(f"AI returned unknown intent: {intent}, defaulting to 'other'")
                state["intent"] = "other"
        except Exception as e:
            logger.error(f"Error in intent classification: {str(e)}")
            state["intent"] = "other"
        return state

    async def calculator_handler(state: EnhancedState) -> EnhancedState:
        latest_message = state["messages"][-1].content
        try:
            result = str(eval(latest_message))
            state["calculation_result"] = result
            logger.info(f"Calculator result: {result} for expression: {latest_message}")
        except Exception as e:
            logger.error(f"Error evaluating calculator expression: {str(e)}")
            state["calculation_result"] = f"Error: Could not calculate '{latest_message}'"
        return state

    async def general_chat_handler(state: EnhancedState) -> EnhancedState:
        logger.info("Processing general chat message")
        return state

    async def generate_response(state: EnhancedState) -> EnhancedState:
        intent = state.get("intent", "other")
        if intent == "calculator" and "calculation_result" in state:
            result = state["calculation_result"]
            response_content = f"The result is: {result}"
            response = {"role": "assistant", "content": response_content}
            logger.info(f"Generated calculator response: {response_content}")
            return {"messages": [response]}
        else:
            start_time = time.time()
            logger.debug("Starting LLM invocation for general chat")
            try:
                response = await llm.ainvoke(state["messages"])
                elapsed = time.time() - start_time
                logger.info(f"LLM responded in {elapsed:.2f}s: {response.content[:100]}...")
                return {"messages": [response]}
            except Exception as e:
                logger.error(f"LLM error: {str(e)}")
                raise

    # Build the graph
    graph_builder = StateGraph(EnhancedState)
    graph_builder.add_node("identify_intent", identify_intent)
    graph_builder.add_node("calculator_handler", calculator_handler)
    graph_builder.add_node("general_chat_handler", general_chat_handler)
    graph_builder.add_node("generate_response", generate_response)
    graph_builder.add_edge(START, "identify_intent")
    graph_builder.add_conditional_edges(
        "identify_intent",
        lambda x: "calculator_handler" if x["intent"] == "calculator" else "general_chat_handler"
    )
    graph_builder.add_edge("calculator_handler", "generate_response")
    graph_builder.add_edge("general_chat_handler", "generate_response")
    graph_builder.add_edge("generate_response", END)
    return graph_builder.compile(checkpointer=checkpointer)
