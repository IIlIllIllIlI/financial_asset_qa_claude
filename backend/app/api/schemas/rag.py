from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    file_name: str
    chunk_count: int
    status: str
