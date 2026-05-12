"""Rerank node — LLM selects best chunks."""

from app.graph.state import GraphState
from app.tools.rerank_tool import rerank_chunks
from app.config.constants import RERANK_N
from app.utils.logger import setup_logger

logger = setup_logger("graph.nodes.rerank")


async def rerank_node(state: GraphState) -> GraphState:
    """Rerank retrieved chunks, select top-N."""
    if state.get("error"):
        return state

    queue = state.get("_token_queue")
    if queue:
        await queue.put({"type": "status", "node": "rerank", "status": "running"})

    retrieved = state.get("retrieved_docs", [])

    try:
        if retrieved:
            ranked = await rerank_chunks(state["user_query"], retrieved, top_n=RERANK_N)
            state["reranked_docs"] = ranked
            logger.info(f"Reranked {len(retrieved)} → {len(ranked)} chunks")
        else:
            state["reranked_docs"] = []
    except Exception as e:
        logger.error(f"Rerank failed: {e}")
        state["error"] = {"type": "LLMError", "message": str(e)}

    return state
