"""Local CrossEncoder rerank tool using BGE-Reranker."""

import asyncio

from sentence_transformers import CrossEncoder

from app.config.settings import get_settings
from app.utils.logger import setup_logger

logger = setup_logger("tools.rerank")

_model: CrossEncoder | None = None


def get_reranker_model() -> CrossEncoder:
    global _model
    if _model is None:
        settings = get_settings()
        logger.info(f"Loading reranker model: {settings.reranker_model}")
        _model = CrossEncoder(settings.reranker_model)
    return _model


async def rerank_chunks(query: str, chunks: list[dict], top_n: int = 4) -> list[dict]:
    """Rerank chunks using local CrossEncoder. Returns top-n most relevant chunks."""
    if not chunks:
        return []

    if len(chunks) <= top_n:
        return chunks

    try:
        model = get_reranker_model()
        pairs = [(query, chunk["content"][:500]) for chunk in chunks]
        scores = await asyncio.to_thread(model.predict, pairs, show_progress_bar=False)

        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        selected = [chunks[i] for i in ranked_indices[:top_n]]

        logger.info(f"Reranked {len(chunks)} → {len(selected)} chunks")
        return selected
    except Exception as e:
        logger.error(f"Rerank failed: {e}")
        return chunks[:top_n]
