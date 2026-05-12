from fastapi import APIRouter
from sqlalchemy import text

from app.api.schemas.common import HealthResponse
from app.database.session import get_engine
from app.vectorstore.chroma_client import get_vector_store
from app.config.settings import get_settings
from app.utils.logger import setup_logger

logger = setup_logger("api.health")
router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    # Check database
    db_status = "disconnected"
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass

    # Check vectorstore
    vectorstore_status = "disconnected"
    try:
        vs = get_vector_store()
        vectorstore_status = "connected"
    except Exception:
        pass

    # Check LLM provider
    llm_status = "unavailable"
    try:
        settings = get_settings()
        if settings.minimax_api_key:
            llm_status = "minimax"
    except Exception:
        pass

    overall = (
        "healthy"
        if db_status == "connected" and vectorstore_status == "connected" and llm_status == "minimax"
        else "degraded"
    )

    return HealthResponse(
        status=overall,
        database=db_status,
        vectorstore=vectorstore_status,
        llm_provider=llm_status,
    )
