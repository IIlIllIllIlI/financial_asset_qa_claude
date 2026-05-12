"""Embedding model tool using BAAI/bge-small-zh-v1.5."""

from langchain_huggingface import HuggingFaceEmbeddings

from app.config.settings import get_settings
from app.utils.logger import setup_logger

logger = setup_logger("tools.embedding")

_model: HuggingFaceEmbeddings | None = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    global _model
    if _model is None:
        settings = get_settings()
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _model


async def embed_text(text: str) -> list[float]:
    """Embed a single text. Returns normalized embedding vector."""
    model = get_embedding_model()
    return await model.aembed_query(text)


async def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts."""
    model = get_embedding_model()
    return await model.aembed_documents(texts)
