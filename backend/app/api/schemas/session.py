from pydantic import BaseModel


class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class ChatMessageSchema(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


class SessionDetailResponse(BaseModel):
    session: SessionResponse
    messages: list[ChatMessageSchema]


class UpdateTitleRequest(BaseModel):
    title: str
