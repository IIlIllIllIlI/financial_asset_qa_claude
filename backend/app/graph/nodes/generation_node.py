"""Response generation node — LLM generates markdown + streams tokens."""

import re

from app.graph.state import GraphState
from app.providers.openai_provider import get_llm_provider
from app.utils.prompt_loader import load_prompt
from app.utils.logger import setup_logger

logger = setup_logger("graph.nodes.generation")


def _build_context(state: GraphState) -> str:
    """Build context string based on intent and available data."""
    context_parts = []

    intent = state.get("intent", "")

    if intent in ("market", "hybrid"):
        market_data = state.get("market_data", {})
        if market_data:
            context_parts.append("## 市场数据")
            for sym, data in market_data.items():
                metrics = data.get("market_metrics", {})
                context_parts.append(
                    f"{sym}: 价格 ${data.get('price')}, "
                    f"涨跌 {data.get('change')} ({data.get('change_pct')}%), "
                    f"PE {metrics.get('pe_ratio', 'N/A')}, "
                    f"市值 {metrics.get('market_cap', 'N/A')}"
                )

    if intent in ("market", "hybrid"):
        news = state.get("news_data", [])
        if news:
            context_parts.append("\n## 相关新闻")
            for i, n in enumerate(news[:5]):
                title = n.get("title", n.get("content", f"新闻 {i+1}"))
                url = n.get("url", "")
                context_parts.append(f"- [{title}]({url})")

        articles = state.get("extracted_articles", [])
        if articles:
            context_parts.append("\n## 新闻详情")
            for a in articles[:2]:
                content = a.get("content", str(a))[:800]
                context_parts.append(content)

    if intent in ("rag", "hybrid"):
        docs = state.get("reranked_docs", [])
        if docs:
            context_parts.append("\n## 知识库内容")
            for i, doc in enumerate(docs):
                meta = doc.get("metadata", {})
                doc_name = meta.get("document_name", f"文档{i+1}")
                context_parts.append(f"**来源: {doc_name}**\n{doc.get('content', '')}")
        else:
            context_parts.append("\n知识库中未找到相关文档。")

    return "\n\n".join(context_parts)


def _extract_citations_from_markdown(text: str, reranked_docs: list) -> list[dict]:
    """Extract citations from markdown source references and reranked docs."""
    citations = []
    seen = set()

    # Pattern: **来源：xxx**
    for m in re.finditer(r"\*\*来源[：:]\s*(.+?)\*\*", text):
        title = m.group(1).strip()
        if title and title not in seen:
            seen.add(title)
            source_type = "rag" if any(
                doc.get("metadata", {}).get("document_name", "") in title for doc in reranked_docs
            ) else "web"
            citations.append({"title": title, "url": "", "source_type": source_type})

    # Pattern: links [title](url)
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        title = m.group(1).strip()
        url = m.group(2).strip()
        if title and title not in seen and url and url.startswith("http"):
            seen.add(title)
            citations.append({"title": title, "url": url, "source_type": "web"})

    # Also add citations from reranked docs
    for doc in reranked_docs:
        meta = doc.get("metadata", {})
        doc_name = meta.get("document_name", "")
        if doc_name and doc_name not in seen:
            seen.add(doc_name)
            citations.append({"title": doc_name, "url": "", "source_type": "rag"})

    return citations


async def generation_node(state: GraphState) -> GraphState:
    """Generate markdown response, stream tokens via _token_queue."""
    if state.get("error"):
        return state

    queue = state.get("_token_queue")
    if queue:
        await queue.put({"type": "status", "node": "generation", "status": "running"})

    provider = get_llm_provider()
    model = provider.get_model()
    intent = state.get("intent", "")

    system_prompt = load_prompt("system/system_prompt.txt")
    context = _build_context(state)
    query = state["user_query"]

    # Build messages
    if intent in ("market", "hybrid"):
        prompt_template = load_prompt("market/market_analysis.txt")
        user_prompt = prompt_template.replace("{market_context}", context)
        user_prompt = user_prompt.replace("{news_context}", "")
        user_prompt = user_prompt.replace("{user_query}", query)
    elif intent == "rag":
        prompt_template = load_prompt("rag/rag_generation.txt")
        user_prompt = prompt_template.replace("{rag_context}", context)
        user_prompt = user_prompt.replace("{user_query}", query)
    else:
        user_prompt = query

    messages = [
        {"role": "system", "content": system_prompt},
    ]
    history = state.get("messages", [])
    if history:
        messages.extend(history[-10:])
    messages.append({"role": "user", "content": user_prompt})

    try:
        full_response = ""

        async for event in model.astream_events(messages, version="v2"):
            kind = event.get("event", "")
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    token = chunk.content
                    full_response += token

                    if queue:
                        await queue.put({"type": "token", "content": token})

        state["answer_markdown"] = full_response

        reranked_docs = state.get("reranked_docs", [])
        state["citations"] = _extract_citations_from_markdown(full_response, reranked_docs)

        logger.info(f"Generation complete: {len(full_response)} chars, {len(state['citations'])} citations")
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        state["error"] = {"type": "LLMError", "message": str(e)}

    return state
