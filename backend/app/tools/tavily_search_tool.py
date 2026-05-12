"""Tavily Search tool wrapper."""

from langchain_tavily import TavilySearch

from app.config.settings import get_settings
from app.config.constants import TAVILY_MAX_RESULTS
from app.utils.logger import setup_logger

logger = setup_logger("tools.tavily_search")


def _get_search_tool() -> TavilySearch:
    settings = get_settings()
    return TavilySearch(
        max_results=TAVILY_MAX_RESULTS,
        tavily_api_key=settings.tavily_api_key,
    )


async def search_news(query: str) -> list[dict]:
    """Search for financial news using Tavily."""
    tool = _get_search_tool()
    search_query = f"{query} stock news"
    logger.info(f"Searching: {search_query}")

    try:
        result = await tool.ainvoke({"query": search_query})
        if isinstance(result, dict):
            return result.get("results", [])
        elif isinstance(result, list):
            return result
        return []
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return []


async def search_ticker_news(tickers: list[str]) -> list[dict]:
    """Search for news for each ticker and merge results."""
    all_results = []
    for ticker in tickers:
        results = await search_news(ticker)
        all_results.extend(results)
    return all_results
