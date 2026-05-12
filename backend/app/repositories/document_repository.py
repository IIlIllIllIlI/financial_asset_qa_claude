import uuid

from sqlalchemy.orm import Session

from app.database.models.knowledge_document import KnowledgeDocument
from app.utils.time import utc_now_iso


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, source: str, chunk_count: int) -> KnowledgeDocument:
        doc = KnowledgeDocument(
            id=str(uuid.uuid4()),
            title=title,
            source=source,
            chunk_count=chunk_count,
            created_at=utc_now_iso(),
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_by_source(self, source: str) -> KnowledgeDocument | None:
        return (
            self.db.query(KnowledgeDocument)
            .filter(KnowledgeDocument.source == source)
            .first()
        )

    def list_all(self) -> list[KnowledgeDocument]:
        return self.db.query(KnowledgeDocument).all()

    def source_already_ingested(self, source: str) -> bool:
        return self.get_by_source(source) is not None
