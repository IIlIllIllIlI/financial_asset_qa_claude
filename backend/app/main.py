"""FastAPI application entry point."""

import uuid
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.database.base import Base
from app.database.session import get_engine, get_session_factory
from app.api.routes import health, sessions, chat, rag
from app.repositories.document_repository import DocumentRepository
from app.services.rag_service import process_file
from app.utils.logger import setup_logger

logger = setup_logger("app.main")


async def auto_ingest_knowledge_base():
    """Auto-ingest knowledge_base/ files on first startup."""
    kb_dir = Path(__file__).parent.parent.parent / "knowledge_base"
    if not kb_dir.exists():
        logger.info("knowledge_base/ directory not found, skipping auto-ingestion")
        return

    supported_extensions = {".pdf", ".md", ".txt"}
    files = [f for f in kb_dir.iterdir() if f.is_file() and f.suffix.lower() in supported_extensions]

    if not files:
        logger.info("No supported files in knowledge_base/")
        return

    settings = get_settings()
    logger.info(f"Found {len(files)} files in knowledge_base/")

    db = get_session_factory()()
    try:
        doc_repo = DocumentRepository(db)

        ingested_count = 0
        for file_path in files:
            filename = file_path.name
            if doc_repo.source_already_ingested(filename):
                logger.info(f"  Already ingested: {filename}")
                continue

            logger.info(f"  Ingesting: {filename} ...")
            try:
                result = await process_file(str(file_path), filename, db)
                logger.info(f"  {filename} → {result['chunk_count']} chunks")
                ingested_count += 1
            except Exception as e:
                logger.error(f"  Failed to ingest {filename}: {e}")

        logger.info(f"Auto-ingestion complete: {ingested_count} new files processed")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")

    # Validate required API keys
    settings = get_settings()
    if not settings.minimax_api_key:
        raise RuntimeError("MINIMAX_API_KEY is not set in .env file")
    if not settings.tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY is not set in .env file")

    Base.metadata.create_all(bind=get_engine())
    logger.info("Database tables created")

    await auto_ingest_knowledge_base()

    logger.info("Startup complete")
    yield
    logger.info("Shutting down...")


app = FastAPI(title="Financial Asset QA System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(rag.router)

logger.info("FastAPI app initialized")
