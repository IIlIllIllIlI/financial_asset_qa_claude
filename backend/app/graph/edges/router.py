"""Conditional edge routing functions."""

from app.graph.state import GraphState


def route_by_intent(state: GraphState) -> str:
    """Route from intent node to first processing node."""
    if state.get("error"):
        return "unsupported"
    intent = state.get("intent", "unsupported")
    if intent == "market":
        return "market"
    elif intent == "rag":
        return "query_rewriter"
    elif intent == "hybrid":
        return "hybrid"
    return "unsupported"


def route_after_extract(state: GraphState) -> str:
    """After extract: market → generation, hybrid → retrieval (RAG phase)."""
    if state.get("error"):
        return "market"
    intent = state.get("intent", "")
    if intent == "hybrid":
        return "query_rewriter"
    return "market"


