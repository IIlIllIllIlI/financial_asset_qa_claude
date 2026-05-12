"""Intent classification node."""

from app.graph.state import GraphState
from app.graph.intent_classifier import classify_intent
from app.providers.openai_provider import get_llm_provider
from app.utils.prompt_loader import load_prompt
from app.utils.logger import setup_logger

logger = setup_logger("graph.nodes.intent")


async def intent_node(state: GraphState) -> GraphState:
    """Classify user intent and set state.intent."""
    if state.get("error"):
        return state

    intent_prompt = load_prompt("intent/intent_classifier.txt")
    provider = get_llm_provider()

    try:
        result = await classify_intent(state["user_query"], provider, intent_prompt)
        state["intent"] = result.intent
        logger.info(f"Intent classified: {result.intent}")
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        state["error"] = {"type": "LLMError", "message": f"Intent classification failed: {e}"}
        state["intent"] = "unsupported"

    return state
