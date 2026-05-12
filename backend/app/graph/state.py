"""LangGraph workflow state definition."""

from typing import TypedDict, Any, Optional


class GraphState(TypedDict):
    """LangGraph workflow state.

    All fields serializable EXCEPT _token_queue, which is injected at
    runtime and used only for real-time SSE token forwarding.
    """

    session_id: str
    user_query: str

    messages: list[dict]

    intent: str

    # RAG
    retrieved_docs: list[dict]
    reranked_docs: list[dict]

    # Market data
    tickers: list[str]
    market_data: dict
    news_data: list[dict]
    extracted_articles: list[dict]

    # Citations
    citations: list[dict]

    # Structured data
    structured_data: dict

    # Final output
    final_response: str
    answer_markdown: str

    # Error state (fail-fast)
    error: Optional[dict]

    # Runtime-only: asyncio.Queue for real-time SSE token forwarding
    _token_queue: Any
