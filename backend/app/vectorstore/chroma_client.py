"""Chroma vector store client using langchain-chroma."""

from pathlib import Path
from langchain_chroma import Chroma

from app.config.settings import get_settings
from app.config.constants import CHROMA_COLLECTION_NAME
from app.tools.embedding_tool import get_embedding_model
from app.utils.logger import setup_logger

logger = setup_logger("vectorstore.chroma")

_vector_store: Chroma | None = None


def get_vector_store() -> Chroma:
    global _vector_store
    if _vector_store is None:
        settings = get_settings()
        chroma_path = Path(settings.chroma_path)
        chroma_path.mkdir(parents=True, exist_ok=True)

        embeddings = get_embedding_model()

        _vector_store = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(chroma_path.resolve()),
        )
        logger.info(f"Chroma vector store initialized at {chroma_path}")
    return _vector_store


def reset_vector_store():
    global _vector_store
    _vector_store = None
