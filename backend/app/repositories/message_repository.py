import uuid
import json

from sqlalchemy.orm import Session

from app.database.models.chat_message import ChatMessage
from app.utils.time import utc_now_iso


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata_dict: dict | None = None,
    ) -> ChatMessage:
        msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            metadata_json=json.dumps(metadata_dict) if metadata_dict else None,
            created_at=utc_now_iso(),
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_by_session_id(self, session_id: str) -> list[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    def get_messages_as_dicts(self, session_id: str) -> list[dict]:
        """Return messages in OpenAI conversation format."""
        messages = self.get_by_session_id(session_id)
        return [{"role": m.role, "content": m.content} for m in messages]

    def delete_by_session_id(self, session_id: str) -> int:
        count = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .delete()
        )
        self.db.commit()
        return count
