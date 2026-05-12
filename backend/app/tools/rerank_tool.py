"""LLM-based rerank tool."""

from pydantic import BaseModel

from app.providers.openai_provider import get_llm_provider
from app.utils.logger import setup_logger

logger = setup_logger("tools.rerank")


class RerankSelection(BaseModel):
    selected_indices: list[int]


async def rerank_chunks(query: str, chunks: list[dict], top_n: int = 4) -> list[dict]:
    """Rerank chunks using LLM. Returns top-n most relevant chunks."""
    if not chunks:
        return []

    if len(chunks) <= top_n:
        return chunks

    provider = get_llm_provider()

    chunks_text = "\n\n".join(
        f"[{i}]\n{chunk['content'][:500]}"
        for i, chunk in enumerate(chunks)
    )

    prompt = f"""从以下文档片段中选择与用户问题最相关的{top_n}个。

用户问题：{query}

文档片段：
{chunks_text}

请输出最相关片段的编号列表（按相关性从高到低排列），例如：[3, 0, 5, 2]
只输出列表，不要输出其他内容。"""

    try:
        structured_llm = provider.with_structured_output(RerankSelection, method="function_calling")
        result = await structured_llm.ainvoke(prompt)

        if isinstance(result, RerankSelection):
            indices = result.selected_indices
        else:
            indices = result.get("selected_indices", []) if isinstance(result, dict) else []

        selected = []
        for idx in indices:
            if isinstance(idx, int) and 0 <= idx < len(chunks):
                selected.append(chunks[idx])

        logger.info(f"Reranked {len(chunks)} → {len(selected)} chunks")
        return selected[:top_n] if selected else chunks[:top_n]
    except Exception as e:
        logger.error(f"Rerank failed: {e}")
        return chunks[:top_n]
