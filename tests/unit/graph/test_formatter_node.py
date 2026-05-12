import pytest

from app.graph.nodes.formatter_node import formatter_node


@pytest.mark.asyncio
async def test_formatter_builds_assets_from_market_data(sample_session_state):
    state = dict(sample_session_state)
    state["tickers"] = ["TSLA"]
    state["market_data"] = {
        "TSLA": {
            "symbol": "TSLA",
            "price": 221.13,
            "change": 5.20,
            "change_pct": 2.4,
            "trend": "bullish",
            "market_metrics": {"market_cap": "692.5B", "pe_ratio": 62.3, "volume": "58.2M"},
            "chart_data": {"7d": [], "30d": []},
        }
    }
    state["citations"] = [{"title": "test", "url": "http://x.com", "source_type": "web"}]

    result = await formatter_node(state)
    sd = result["structured_data"]
    assert len(sd["assets"]) == 1
    assert sd["assets"][0]["symbol"] == "TSLA"
    assert sd["assets"][0]["price"] == 221.13
    assert len(result["citations"]) == 1


@pytest.mark.asyncio
async def test_formatter_empty_on_no_market_data(sample_session_state):
    result = await formatter_node(sample_session_state)
    assert result["structured_data"]["assets"] == []


@pytest.mark.asyncio
async def test_formatter_skips_on_error(sample_session_state):
    state = dict(sample_session_state, error={"type": "TestError", "message": "test"})
    result = await formatter_node(state)
    assert result["error"] is not None
