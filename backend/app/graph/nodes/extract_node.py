"""Extract node — Tavily Extract full article text."""

from app.graph.state import GraphState
from app.tools.tavily_extract_tool import extract_articles
from app.utils.logger import setup_logger

logger = setup_logger("graph.nodes.extract")


async def extract_node(state: GraphState) -> GraphState:
    """Extract full article text from top news URLs."""
    if state.get("error"):
        return state

    queue = state.get("_token_queue")
    if queue:
        await queue.put({"type": "status", "node": "extract", "status": "running"})

    news_data = state.get("news_data", [])

    try:
        urls = [n.get("url") for n in news_data if n.get("url")]
        if urls:
            articles = await extract_articles(urls)
            state["extracted_articles"] = articles
            logger.info(f"Articles extracted: {len(articles)}")
        else:
            state["extracted_articles"] = []
    except Exception as e:
        logger.error(f"Article extraction failed: {e}")
        state["error"] = {"type": "TavilyError", "message": str(e)}

    return state
