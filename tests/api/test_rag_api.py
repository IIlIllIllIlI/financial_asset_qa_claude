"""RAG Upload API tests."""
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


class TestRAGUploadAPI:

    @patch("app.api.routes.rag.process_file")
    def test_upload_pdf(self, mock_process, client):
        """Upload a PDF file should return chunk count."""
        mock_process.return_value = {
            "document_id": "doc-123",
            "file_name": "test.pdf",
            "chunk_count": 3,
            "status": "completed",
        }
        res = client.post(
            "/api/rag/upload",
            files={"file": ("test.pdf", b"fake pdf content", "application/pdf")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["file_name"] == "test.pdf"
        assert data["chunk_count"] == 3

    @patch("app.api.routes.rag.process_file")
    def test_upload_markdown(self, mock_process, client):
        """Upload a .md file should work."""
        mock_process.return_value = {
            "document_id": "doc-456",
            "file_name": "test.md",
            "chunk_count": 1,
            "status": "completed",
        }
        res = client.post(
            "/api/rag/upload",
            files={"file": ("test.md", b"# Hello\n\nWorld", "text/markdown")},
        )
        assert res.status_code == 200
        assert res.json()["chunk_count"] == 1

    def test_upload_unsupported_type(self, client):
        """Upload a .jpg should return 400."""
        res = client.post(
            "/api/rag/upload",
            files={"file": ("photo.jpg", b"fake jpg", "image/jpeg")},
        )
        assert res.status_code == 400
        assert "Unsupported" in res.json()["detail"]

    def test_upload_no_file(self, client):
        """Upload without file should return 422."""
        res = client.post("/api/rag/upload")
        assert res.status_code == 422
