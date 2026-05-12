from sqlalchemy import Column, String

from app.database.base import Base


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(String, primary_key=True)
    file_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    error_message = Column(String)
    created_at = Column(String, nullable=False)
