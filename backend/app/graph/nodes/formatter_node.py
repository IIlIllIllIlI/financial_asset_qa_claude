"""Formatter node — builds structured_data from real market data, normalizes citations."""

from app.graph.state import GraphState
from app.utils.logger import setup_logger

logger = setup_logger("graph.nodes.formatter")


async def formatter_node(state: GraphState) -> GraphState:
    """Build structured_data.assets[] from state.market_data (real yfinance data)."""
    if state.get("error"):
        return state

    market_data = state.get("market_data", {})
    tickers = state.get("tickers", [])

    assets = []
    for ticker in tickers:
        data = market_data.get(ticker, {})
        if data:
            assets.append({
                "symbol": data.get("symbol", ticker),
                "price": data.get("price"),
                "change": data.get("change"),
                "change_pct": data.get("change_pct"),
                "trend": data.get("trend"),
                "market_metrics": data.get("market_metrics", {}),
                "chart_data": data.get("chart_data", {}),
            })

    state["structured_data"] = {"assets": assets}

    # Normalize citations
    citations = state.get("citations", [])
    normalized = []
    for c in citations:
        if isinstance(c, dict):
            normalized.append({
                "title": c.get("title", ""),
                "url": c.get("url", ""),
                "source_type": c.get("source_type", "web"),
            })
    state["citations"] = normalized

    state["final_response"] = state.get("answer_markdown", "")
    logger.info(f"Formatter complete: {len(assets)} assets, {len(normalized)} citations")
    return state
