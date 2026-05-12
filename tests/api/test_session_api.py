"""Session API tests using FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.base import Base
from app.database.session import get_engine, get_session_factory


@pytest.fixture
def client():
    Base.metadata.create_all(bind=get_engine())
    with TestClient(app) as c:
        yield c
    # Cleanup handled by test isolation


class TestSessionAPI:
    def test_create_session(self, client):
        res = client.post("/api/sessions")
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["title"] == "新对话"
        assert "created_at" in data

    def test_list_sessions(self, client):
        client.post("/api/sessions")
        client.post("/api/sessions")
        res = client.get("/api/sessions")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_get_session(self, client):
        create_res = client.post("/api/sessions")
        session_id = create_res.json()["id"]

        res = client.get(f"/api/sessions/{session_id}")
        assert res.status_code == 200
        data = res.json()
        assert "session" in data
        assert "messages" in data

    def test_get_session_not_found(self, client):
        res = client.get("/api/sessions/nonexistent")
        assert res.status_code == 404

    def test_update_title(self, client):
        create_res = client.post("/api/sessions")
        session_id = create_res.json()["id"]

        res = client.patch(
            f"/api/sessions/{session_id}/title",
            json={"title": "新标题测试"},
        )
        assert res.status_code == 200
        assert res.json()["title"] == "新标题测试"

    def test_delete_session(self, client):
        create_res = client.post("/api/sessions")
        session_id = create_res.json()["id"]

        res = client.delete(f"/api/sessions/{session_id}")
        assert res.status_code == 204

        # Verify deleted
        res = client.get(f"/api/sessions/{session_id}")
        assert res.status_code == 404
