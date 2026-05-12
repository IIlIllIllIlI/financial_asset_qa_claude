import uuid

from sqlalchemy.orm import Session

from app.database.models.ingestion_job import IngestionJob
from app.utils.time import utc_now_iso


class IngestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, file_name: str, status: str = "pending") -> IngestionJob:
        job = IngestionJob(
            id=str(uuid.uuid4()),
            file_name=file_name,
            status=status,
            created_at=utc_now_iso(),
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_status(
        self, job_id: str, status: str, error_message: str | None = None
    ) -> IngestionJob | None:
        job = self.db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if job is None:
            return None
        job.status = status
        if error_message:
            job.error_message = error_message
        self.db.commit()
        self.db.refresh(job)
        return job
