from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: dict


class HealthResponse(BaseModel):
    status: str
    database: str
    vectorstore: str
    llm_provider: str
