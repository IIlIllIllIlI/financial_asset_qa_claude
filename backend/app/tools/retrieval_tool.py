"""Chroma vector search tool."""

from app.tools.embedding_tool import get_embedding_model
from app.vectorstore.chroma_client import get_vector_store
from app.config.constants import RETRIEVAL_K
from app.utils.logger import setup_logger

logger = setup_logger("tools.retrieval")


async def retrieve_chunks(query: str) -> list[dict]:
    """Search Chroma for top-k relevant chunks."""
    vector_store = get_vector_store()
    try:
        results = vector_store.similarity_search_with_score(
            query, k=RETRIEVAL_K
        )
        chunks = []
        for doc, score in results:
            chunks.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
            })
        logger.info(f"Retrieved {len(chunks)} chunks for query")
        return chunks
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return []
