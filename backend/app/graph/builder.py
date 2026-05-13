"""LangGraph builder — creates and compiles the workflow graph."""

from langgraph.graph import StateGraph, END

from app.graph.state import GraphState
from app.graph.nodes.intent_node import intent_node
from app.graph.nodes.query_rewriter_node import query_rewriter_node
from app.graph.nodes.market_node import market_node
from app.graph.nodes.news_node import news_node
from app.graph.nodes.extract_node import extract_node
from app.graph.nodes.retrieval_node import retrieval_node
from app.graph.nodes.rerank_node import rerank_node
from app.graph.nodes.generation_node import generation_node
from app.graph.nodes.formatter_node import formatter_node
from app.graph.nodes.rejection_node import rejection_node
from app.graph.edges.router import route_by_intent, route_after_extract
from app.utils.logger import setup_logger

logger = setup_logger("graph.builder")

_compiled_graph = None


def create_graph() -> StateGraph:
    """Create the full LangGraph workflow."""
    workflow = StateGraph(GraphState)

    # Register nodes
    workflow.add_node("intent", intent_node)
    workflow.add_node("query_rewriter", query_rewriter_node)
    workflow.add_node("market_data", market_node)
    workflow.add_node("news", news_node)
    workflow.add_node("extract", extract_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("rerank", rerank_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("formatter", formatter_node)
    workflow.add_node("rejection", rejection_node)

    # Entry
    workflow.set_entry_point("intent")

    # After intent: route to first node based on intent
    workflow.add_conditional_edges(
        "intent",
        route_by_intent,
        {
            "market": "market_data",
            "query_rewriter": "query_rewriter",
            "hybrid": "market_data",
            "unsupported": "rejection",
        },
    )

    # market_data → news (shared by market and hybrid)
    workflow.add_edge("market_data", "news")

    # news → extract (shared by market and hybrid)
    workflow.add_edge("news", "extract")

    # After extract: market → generation, hybrid → query_rewriter
    workflow.add_conditional_edges(
        "extract",
        route_after_extract,
        {
            "market": "generation",
            "query_rewriter": "query_rewriter",
        },
    )

    # query_rewriter → retrieval (both rag and hybrid)
    workflow.add_edge("query_rewriter", "retrieval")

    # retrieval → rerank (shared by rag and hybrid)
    workflow.add_edge("retrieval", "rerank")

    # rerank → generation (both rag and hybrid paths converge here)
    workflow.add_edge("rerank", "generation")

    # generation → formatter → END (all flows)
    workflow.add_edge("generation", "formatter")
    workflow.add_edge("formatter", END)

    # rejection → END
    workflow.add_edge("rejection", END)

    logger.info("LangGraph workflow created")
    return workflow


def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        workflow = create_graph()
        _compiled_graph = workflow.compile(checkpointer=False)
        logger.info("LangGraph compiled")

        from app.utils.graph_viz import show_graph_image
        show_graph_image(_compiled_graph)

    return _compiled_graph
