from sqlalchemy import Column, String, Integer

from app.database.base import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    chunk_count = Column(Integer, nullable=False)
    created_at = Column(String, nullable=False)
