from sqlalchemy import Column, String

from app.database.base import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False, default="新对话")
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
