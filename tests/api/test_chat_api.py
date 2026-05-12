"""Chat API tests using FastAPI TestClient with mocked LangGraph."""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.database.base import Base
from app.database.session import get_engine


@pytest.fixture
def client():
    Base.metadata.create_all(bind=get_engine())
    with TestClient(app) as c:
        yield c


class TestChatAPI:
    """Test chat API non-streaming mode."""

    def _create_session(self, client):
        res = client.post("/api/sessions")
        assert res.status_code == 201
        return res.json()["id"]

    @patch("app.api.routes.chat.get_compiled_graph")
    def test_chat_market_non_streaming(self, mock_graph, client):
        """Non-streaming chat with market intent should return 200."""
        mock_compiled = AsyncMock()
        mock_compiled.ainvoke.return_value = {
            "answer_markdown": "# TSLA Analysis\n\nPrice: $430.00",
            "structured_data": {
                "assets": [{"symbol": "TSLA", "price": 430.00, "change": -5.00, "change_pct": -1.15}]
            },
            "citations": [{"title": "Yahoo Finance", "url": "https://finance.yahoo.com", "source_type": "web"}],
            "intent": "market",
            "error": None,
        }
        mock_graph.return_value = mock_compiled

        session_id = self._create_session(client)
        res = client.post("/api/chat", json={
            "session_id": session_id,
            "query": "特斯拉股价？",
            "stream": False,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["answer_markdown"] == "# TSLA Analysis\n\nPrice: $430.00"
        assert len(data["structured_data"]["assets"]) == 1
        assert data["structured_data"]["assets"][0]["price"] == 430.00
        assert len(data["citations"]) == 1
        assert data["metadata"]["intent"] == "market"
        assert "processing_time_ms" in data["metadata"]

    @patch("app.api.routes.chat.get_compiled_graph")
    def test_chat_rag_non_streaming(self, mock_graph, client):
        """Non-streaming chat with RAG intent should return 200."""
        mock_compiled = AsyncMock()
        mock_compiled.ainvoke.return_value = {
            "answer_markdown": "# P/E Ratio\n\n市盈率是...",
            "structured_data": {"assets": []},
            "citations": [{"title": "pe_ratio.md", "url": "", "source_type": "rag"}],
            "intent": "rag",
            "error": None,
        }
        mock_graph.return_value = mock_compiled

        session_id = self._create_session(client)
        res = client.post("/api/chat", json={
            "session_id": session_id,
            "query": "什么是市盈率？",
            "stream": False,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["metadata"]["intent"] == "rag"
        assert len(data["citations"]) == 1
        assert data["citations"][0]["source_type"] == "rag"

    @patch("app.api.routes.chat.get_compiled_graph")
    def test_chat_unsupported_non_streaming(self, mock_graph, client):
        """Non-streaming chat with unsupported intent."""
        mock_compiled = AsyncMock()
        mock_compiled.ainvoke.return_value = {
            "answer_markdown": "抱歉，我无法回答这个问题...",
            "structured_data": {"assets": []},
            "citations": [],
            "intent": "unsupported",
            "error": None,
        }
        mock_graph.return_value = mock_compiled

        session_id = self._create_session(client)
        res = client.post("/api/chat", json={
            "session_id": session_id,
            "query": "今天天气怎么样？",
            "stream": False,
        })
        assert res.status_code == 200
        assert res.json()["metadata"]["intent"] == "unsupported"

    @patch("app.api.routes.chat.get_compiled_graph")
    def test_chat_graph_error_propagation(self, mock_graph, client):
        """When graph returns error, API should return 502."""
        mock_compiled = AsyncMock()
        mock_compiled.ainvoke.return_value = {
            "answer_markdown": "",
            "structured_data": {"assets": []},
            "citations": [],
            "intent": "",
            "error": {"type": "MarketAPIError", "message": "Failed to fetch data"},
        }
        mock_graph.return_value = mock_compiled

        session_id = self._create_session(client)
        res = client.post("/api/chat", json={
            "session_id": session_id,
            "query": "特斯拉股价？",
            "stream": False,
        })
        assert res.status_code == 502
        assert "MarketAPIError" in res.json()["detail"]

    def test_chat_session_not_found(self, client):
        """Chat with invalid session should return 404."""
        res = client.post("/api/chat", json={
            "session_id": "nonexistent-id",
            "query": "测试",
            "stream": False,
        })
        assert res.status_code == 404
