"""Market data node — Yahoo Finance."""

from app.graph.state import GraphState
from app.tools.market_data_tool import extract_tickers, fetch_all_market_data
from app.providers.openai_provider import get_llm_provider
from app.utils.logger import setup_logger

logger = setup_logger("graph.nodes.market")


async def market_node(state: GraphState) -> GraphState:
    """Fetch market data for detected tickers."""
    if state.get("error"):
        return state

    queue = state.get("_token_queue")
    if queue:
        await queue.put({"type": "status", "node": "market_data", "status": "running"})

    provider = get_llm_provider()
    model = provider.get_model()
    query = state["user_query"]

    try:
        tickers = await extract_tickers(query, model)
        if not tickers:
            logger.warning("No tickers extracted from query")
            state["tickers"] = []
            state["market_data"] = {}
            return state

        state["tickers"] = tickers
        logger.info(f"Tickers extracted: {tickers}")

        market_data = await fetch_all_market_data(tickers)
        state["market_data"] = market_data
        logger.info(f"Market data fetched for {list(market_data.keys())}")
    except Exception as e:
        logger.error(f"Market data fetch failed: {e}")
        state["error"] = {"type": "MarketAPIError", "message": str(e)}

    return state
