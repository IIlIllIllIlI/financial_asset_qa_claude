"""Tavily Extract tool wrapper."""

from langchain_tavily import TavilyExtract

from app.config.settings import get_settings
from app.utils.logger import setup_logger

logger = setup_logger("tools.tavily_extract")


def _get_extract_tool() -> TavilyExtract:
    settings = get_settings()
    return TavilyExtract(
        tavily_api_key=settings.tavily_api_key,
        extract_depth="advanced",
        format="markdown",
    )


async def extract_articles(urls: list[str]) -> list[dict]:
    """Extract full article text from URLs using Tavily Extract."""
    if not urls:
        return []

    tool = _get_extract_tool()
    logger.info(f"Extracting content from {len(urls)} URLs")

    try:
        results = []
        for url in urls[:2]:  # Top 2 per ticker
            extracted = await tool.ainvoke({"urls": [url]})
            if isinstance(extracted, list):
                results.extend(extracted)
            elif isinstance(extracted, dict):
                results.append(extracted)
        return results
    except Exception as e:
        logger.error(f"Tavily extract failed: {e}")
        return []
