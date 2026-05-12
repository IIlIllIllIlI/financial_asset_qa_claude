from sqlalchemy import Column, String, ForeignKey, Text

from app.database.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text)
    created_at = Column(String, nullable=False)
