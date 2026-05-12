import pytest
from unittest.mock import AsyncMock, patch

from app.graph.nodes.intent_node import intent_node


@pytest.mark.asyncio
async def test_intent_node_classifies_market(sample_session_state):
    with patch(
        "app.graph.nodes.intent_node.classify_intent",
        new=AsyncMock(return_value=type("IntentResult", (), {"intent": "market"})()),
    ):
        result = await intent_node(sample_session_state)
        assert result["intent"] == "market"
        assert result.get("error") is None


@pytest.mark.asyncio
async def test_intent_node_classifies_rag(sample_session_state):
    with patch(
        "app.graph.nodes.intent_node.classify_intent",
        new=AsyncMock(return_value=type("IntentResult", (), {"intent": "rag"})()),
    ):
        result = await intent_node(sample_session_state)
        assert result["intent"] == "rag"


@pytest.mark.asyncio
async def test_intent_node_skips_on_error(sample_session_state):
    state = dict(sample_session_state, error={"type": "LLMError", "message": "test"})
    result = await intent_node(state)
    assert result["error"] is not None
    assert result["intent"] == ""  # not modified


@pytest.mark.asyncio
async def test_intent_node_handles_exception(sample_session_state):
    with patch(
        "app.graph.nodes.intent_node.classify_intent",
        new=AsyncMock(side_effect=Exception("LLM down")),
    ):
        result = await intent_node(sample_session_state)
        assert result["error"] is not None
        assert result["error"]["type"] == "LLMError"
        assert result["intent"] == "unsupported"
