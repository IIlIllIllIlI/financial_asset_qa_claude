"""Chat API — POST /api/chat with SSE streaming and non-streaming support."""

import json
import time
import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.api.schemas.common import ErrorResponse
from app.database.session import get_db, get_session_factory
from app.graph.state import GraphState
from app.graph.builder import get_compiled_graph
from app.services.session_service import SessionService
from app.services.title_generation_service import generate_and_update_title
from app.utils.logger import setup_logger

logger = setup_logger("api.chat")
router = APIRouter(tags=["chat"])


def _build_initial_state(request: ChatRequest, messages: list[dict], token_queue: asyncio.Queue) -> dict:
    return {
        "session_id": request.session_id,
        "user_query": request.query,
        "messages": messages,
        "intent": "",
        "retrieved_docs": [],
        "reranked_docs": [],
        "tickers": [],
        "market_data": {},
        "news_data": [],
        "extracted_articles": [],
        "citations": [],
        "structured_data": {"assets": []},
        "final_response": "",
        "answer_markdown": "",
        "error": None,
        "_token_queue": token_queue,
    }


async def _run_graph(initial_state: dict) -> None:
    """Run the LangGraph workflow and send results to the token queue."""
    compiled_graph = get_compiled_graph()
    queue = initial_state["_token_queue"]
    try:
        result = await compiled_graph.ainvoke(initial_state)

        graph_error = result.get("error")
        if graph_error:
            await queue.put({
                "type": "error",
                "error": graph_error,
            })
            return

        await queue.put({
            "type": "done",
            "answer_markdown": result.get("answer_markdown", ""),
            "structured_data": result.get("structured_data", {"assets": []}),
            "citations": result.get("citations", []),
            "session_id": result.get("session_id", ""),
        })
    except Exception as e:
        logger.error(f"Graph execution failed: {e}", exc_info=True)
        await queue.put({
            "type": "error",
            "error": {"type": type(e).__name__, "message": str(e)},
        })


@router.post("/api/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    session_service = SessionService(db)

    session = session_service.session_repo.get_by_id(request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = session_service.get_conversation_history(request.session_id)

    if request.stream:
        token_queue: asyncio.Queue = asyncio.Queue()
        initial_state = _build_initial_state(request, messages, token_queue)

        async def event_stream():
            task = asyncio.create_task(_run_graph(initial_state))

            while True:
                item = await token_queue.get()
                item_type = item.get("type")

                if item_type == "status":
                    yield f"event: status\ndata: {json.dumps({'node': item['node'], 'status': item['status']})}\n\n"

                elif item_type == "token":
                    yield f"event: token\ndata: {json.dumps({'content': item['content']})}\n\n"

                elif item_type == "done":
                    yield f"event: structured_data\ndata: {json.dumps(item['structured_data'])}\n\n"
                    yield f"event: citations\ndata: {json.dumps({'citations': item['citations']})}\n\n"
                    yield f"event: done\ndata: {json.dumps({'session_id': item['session_id']})}\n\n"

                    # Persist messages
                    final_answer = item.get("answer_markdown", "")
                    final_structured = item.get("structured_data", {})
                    final_citations = item.get("citations", [])
                    session_service.persist_chat_turn(
                        request.session_id,
                        request.query,
                        final_answer,
                        {"structured_data": final_structured, "citations": final_citations},
                    )

                    # Fire-and-forget title generation if this is the first message
                    msg_count = len(session_service.message_repo.get_by_session_id(request.session_id))
                    if msg_count <= 2:  # Only this turn exists
                        asyncio.create_task(
                            generate_and_update_title(
                                request.session_id,
                                request.query,
                                final_answer,
                                get_session_factory,
                            )
                        )

                    break

                elif item_type == "error":
                    error_info = item.get("error", {})
                    yield f"event: error\ndata: {json.dumps({'error': error_info})}\n\n"
                    break

            await task

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # Non-streaming mode
    token_queue: asyncio.Queue = asyncio.Queue()
    initial_state = _build_initial_state(request, messages, token_queue)

    start_time = time.time()

    compiled_graph = get_compiled_graph()
    try:
        result = await compiled_graph.ainvoke(initial_state)
    except Exception as e:
        logger.error(f"Non-streaming graph execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    processing_time_ms = int((time.time() - start_time) * 1000)

    # Check for node-level errors
    graph_error = result.get("error")
    if graph_error:
        raise HTTPException(
            status_code=502,
            detail=f"{graph_error.get('type', 'Error')}: {graph_error.get('message', 'Unknown error')}",
        )

    answer = result.get("answer_markdown", "")
    structured_data = result.get("structured_data", {"assets": []})
    citations = result.get("citations", [])

    session_service.persist_chat_turn(
        request.session_id,
        request.query,
        answer,
        {"structured_data": structured_data, "citations": citations},
    )

    msg_count = len(session_service.message_repo.get_by_session_id(request.session_id))
    if msg_count <= 2:
        asyncio.create_task(
            generate_and_update_title(
                request.session_id,
                request.query,
                answer,
                get_session_factory,
            )
        )

    return ChatResponse(
        answer_markdown=answer,
        structured_data=structured_data,
        citations=citations,
        metadata={
            "session_id": request.session_id,
            "intent": result.get("intent", ""),
            "processing_time_ms": processing_time_ms,
        },
    )
