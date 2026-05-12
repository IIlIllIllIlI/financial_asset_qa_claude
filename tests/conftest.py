"""Shared fixtures for all tests."""

import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend/app is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database.base import Base


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_session_state():
    """Return a minimal GraphState for testing."""
    return {
        "session_id": "test-session-id",
        "user_query": "特斯拉当前股价是多少？",
        "messages": [],
        "intent": "",
        "retrieved_docs": [],
        "reranked_docs": [],
        "tickers": [],
        "market_data": {},
        "news_data": [],
        "extracted_articles": [],
        "citations": [],
        "structured_data": {"assets": []},
        "final_response": "",
        "answer_markdown": "",
        "error": None,
        "_token_queue": None,
    }
