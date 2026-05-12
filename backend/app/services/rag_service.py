"""RAG document processing service."""

import uuid
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.constants import CHUNK_SIZE, CHUNK_OVERLAP
from app.vectorstore.chroma_client import get_vector_store
from app.repositories.document_repository import DocumentRepository
from app.repositories.ingestion_repository import IngestionRepository
from app.utils.logger import setup_logger

logger = setup_logger("services.rag")


async def process_file(
    file_path: str,
    original_filename: str,
    db,
) -> dict:
    """Parse, chunk, embed, and store a document file. Returns result dict."""
    file_path_obj = Path(file_path)
    suffix = file_path_obj.suffix.lower()

    doc_repo = DocumentRepository(db)
    ingestion_repo = IngestionRepository(db)

    job = ingestion_repo.create(original_filename, "processing")

    try:
        # Parse
        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path_obj))
        else:
            loader = TextLoader(str(file_path_obj), encoding="utf-8")

        documents = loader.load()

        # Chunk
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "，", " ", ""],
        )
        chunks = text_splitter.split_documents(documents)

        # Add metadata
        doc_id = str(uuid.uuid4())
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "document_id": doc_id,
                "document_name": original_filename,
                "chunk_index": i,
                "source": "uploaded",
            })

        # Store in Chroma
        vector_store = get_vector_store()
        vector_store.add_documents(chunks)

        # Create document record
        doc_record = doc_repo.create(
            title=original_filename,
            source=original_filename,
            chunk_count=len(chunks),
        )

        ingestion_repo.update_status(job.id, "completed")

        logger.info(f"RAG ingestion complete: {original_filename} → {len(chunks)} chunks")
        return {
            "document_id": doc_record.id,
            "file_name": original_filename,
            "chunk_count": len(chunks),
            "status": "completed",
        }

    except Exception as e:
        logger.error(f"RAG ingestion failed for {original_filename}: {e}")
        ingestion_repo.update_status(job.id, "failed", str(e))
        raise
