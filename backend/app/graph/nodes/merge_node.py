"""Merge node — LLM synthesizes market + news + RAG context (hybrid only)."""

from app.graph.state import GraphState
from app.providers.openai_provider import get_llm_provider
from app.utils.logger import setup_logger

logger = setup_logger("graph.nodes.merge")


async def merge_node(state: GraphState) -> GraphState:
    """Synthesize all gathered context into a coherent summary (hybrid flow)."""
    if state.get("error"):
        return state

    queue = state.get("_token_queue")
    if queue:
        await queue.put({"type": "status", "node": "merge", "status": "running"})

    market_data = state.get("market_data", {})
    news_data = state.get("news_data", [])
    extracted_articles = state.get("extracted_articles", [])
    reranked_docs = state.get("reranked_docs", [])
    query = state["user_query"]

    market_context = ""
    if market_data:
        for symbol, data in market_data.items():
            market_context += f"\n{symbol}: 价格 ${data.get('price')}, 涨跌 {data.get('change')} ({data.get('change_pct')}%), PE {data.get('market_metrics', {}).get('pe_ratio', 'N/A')}"

    news_context = ""
    for n in news_data:
        title = n.get("title", "") or n.get("content", "")[:100] if n.get("content") else ""
        news_context += f"\n- {title}"

    article_context = ""
    for a in extracted_articles:
        content = a.get("content", "") if isinstance(a, dict) else str(a)
        article_context += f"\n{content[:500]}"

    rag_context = ""
    for doc in reranked_docs:
        rag_context += f"\n- {doc.get('content', '')[:300]}"

    merge_prompt = f"""将以下所有信息整合为一份简洁的上下文摘要，用于生成最终回答。

用户问题：{query}

## 市场数据
{market_context or '无'}

## 新闻
{news_context or '无'}

## 文章内容
{article_context or '无'}

## 知识库内容
{rag_context or '无'}

请生成一份整合的上下文摘要（不超过500字），后续将基于此摘要生成最终回答。"""

    try:
        provider = get_llm_provider()
        model = provider.get_model()
        result = await model.ainvoke(merge_prompt)
        summary = result.content if hasattr(result, "content") else str(result)
        state["_merged_context"] = summary  # Will be used by generation_node
        logger.info("Merge complete")
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        state["error"] = {"type": "LLMError", "message": str(e)}

    return state
