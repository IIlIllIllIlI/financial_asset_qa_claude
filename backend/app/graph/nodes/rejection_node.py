"""Rejection node — friendly rejection for unsupported queries."""

from app.graph.state import GraphState
from app.providers.openai_provider import get_llm_provider
from app.utils.prompt_loader import load_prompt
from app.utils.logger import setup_logger
from app.utils.text import strip_thinking

logger = setup_logger("graph.nodes.rejection")


async def rejection_node(state: GraphState) -> GraphState:
    """Generate friendly rejection message for unsupported queries."""
    if state.get("error"):
        return state

    queue = state.get("_token_queue")

    prompt_template = load_prompt("rejection/unsupported_query.txt")
    prompt = prompt_template.replace("{user_query}", state["user_query"])

    provider = get_llm_provider()
    model = provider.get_model()

    try:
        full_response = ""
        async for event in model.astream_events(
            [{"role": "user", "content": prompt}], version="v2"
        ):
            kind = event.get("event", "")
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    full_response += chunk.content
                    if queue:
                        await queue.put({"type": "token", "content": chunk.content})

        cleaned = strip_thinking(full_response)
        state["answer_markdown"] = cleaned
        state["final_response"] = cleaned
        state["structured_data"] = {"assets": []}
        state["citations"] = []
        logger.info("Rejection response generated")
    except Exception as e:
        logger.error(f"Rejection generation failed: {e}")
        state["error"] = {"type": "LLMError", "message": str(e)}

    return state
