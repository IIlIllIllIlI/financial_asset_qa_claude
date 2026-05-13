"""Query rewriting node — optimizes user query for vector retrieval."""

from app.graph.state import GraphState
from app.providers.openai_provider import get_llm_provider
from app.utils.prompt_loader import load_prompt
from app.utils.logger import setup_logger

logger = setup_logger("graph.nodes.query_rewriter")


def _build_chat_history(messages: list[dict]) -> str:
    """Build a brief chat history summary for context-aware rewriting."""
    if not messages:
        return ""
    recent = messages[-6:]  # last 3 user-assistant pairs
    lines = ["对话历史："]
    for msg in recent:
        role = "用户" if msg.get("role") == "user" else "助手"
        content = msg.get("content", "")
        lines.append(f"{role}: {content[:200]}")
    return "\n".join(lines)


async def query_rewriter_node(state: GraphState) -> GraphState:
    """Rewrite the user query to improve vector search recall."""
    if state.get("error"):
        return state

    queue = state.get("_token_queue")
    if queue:
        await queue.put({"type": "status", "node": "query_rewriter", "status": "running"})

    try:
        prompt_template = load_prompt("rag/query_rewriter.txt")
        chat_history = _build_chat_history(state.get("messages", []))
        prompt = prompt_template.format(
            user_query=state["user_query"],
            chat_history=chat_history,
        )

        provider = get_llm_provider()
        result = await provider.chat([{"role": "user", "content": prompt}])
        rewritten = result.content.strip() if hasattr(result, "content") else str(result).strip()

        if rewritten:
            state["rewritten_query"] = rewritten
            logger.info(f"Query rewritten: '{state['user_query']}' → '{rewritten}'")
        else:
            state["rewritten_query"] = state["user_query"]
    except Exception as e:
        logger.warning(f"Query rewriting failed, falling back to original: {e}")
        state["rewritten_query"] = state["user_query"]

    return state
