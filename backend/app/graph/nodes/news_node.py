"""News search node — Tavily Search."""

from app.graph.state import GraphState
from app.tools.tavily_search_tool import search_ticker_news
from app.utils.logger import setup_logger

logger = setup_logger("graph.nodes.news")


async def news_node(state: GraphState) -> GraphState:
    """Search for news about tickers."""
    if state.get("error"):
        return state

    queue = state.get("_token_queue")
    if queue:
        await queue.put({"type": "status", "node": "news", "status": "running"})

    tickers = state.get("tickers", [])

    try:
        if tickers:
            news = await search_ticker_news(tickers)
            state["news_data"] = news
            logger.info(f"News fetched: {len(news)} results")
        else:
            state["news_data"] = []
    except Exception as e:
        logger.error(f"News search failed: {e}")
        state["error"] = {"type": "TavilyError", "message": str(e)}

    return state
