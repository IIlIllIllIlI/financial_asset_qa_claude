"""Retrieval node — Chroma similarity search."""

from app.graph.state import GraphState
from app.tools.retrieval_tool import retrieve_chunks
from app.utils.logger import setup_logger

logger = setup_logger("graph.nodes.retrieval")


async def retrieval_node(state: GraphState) -> GraphState:
    """Search Chroma for relevant document chunks."""
    if state.get("error"):
        return state

    queue = state.get("_token_queue")
    if queue:
        await queue.put({"type": "status", "node": "retrieval", "status": "running"})

    try:
        query = state.get("rewritten_query") or state["user_query"]
        chunks = await retrieve_chunks(query)
        state["retrieved_docs"] = chunks
        logger.info(f"Retrieved {len(chunks)} chunks")
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        state["error"] = {"type": "RetrievalError", "message": str(e)}

    return state
