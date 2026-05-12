import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.base import Base
from app.database.session import get_engine


@pytest.fixture
def client():
    Base.metadata.create_all(bind=get_engine())
    with TestClient(app) as c:
        yield c


class TestHealthAPI:
    def test_health_check(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert "database" in data
        assert "vectorstore" in data
        assert "llm_provider" in data
