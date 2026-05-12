"""Session lifecycle management service."""

from sqlalchemy.orm import Session

from app.repositories.session_repository import SessionRepository
from app.repositories.message_repository import MessageRepository
from app.utils.time import utc_now_iso
from app.utils.logger import setup_logger

logger = setup_logger("services.session")


class SessionService:
    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.message_repo = MessageRepository(db)

    def create_session(self) -> dict:
        session = self.session_repo.create()
        return {
            "id": session.id,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
        }

    def get_session_with_messages(self, session_id: str) -> dict | None:
        session = self.session_repo.get_by_id(session_id)
        if session is None:
            return None

        messages = self.message_repo.get_by_session_id(session_id)
        return {
            "session": {
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
            },
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at,
                }
                for m in messages
            ],
        }

    def persist_chat_turn(
        self,
        session_id: str,
        user_query: str,
        assistant_content: str,
        metadata_dict: dict | None = None,
    ):
        """Persist both user message and assistant response."""
        self.message_repo.create(session_id, "user", user_query)
        self.message_repo.create(session_id, "assistant", assistant_content, metadata_dict)
        self.session_repo.update_timestamp(session_id)
        logger.info(f"Chat turn persisted for session {session_id}")

    def get_conversation_history(self, session_id: str) -> list[dict]:
        """Get messages in OpenAI conversation format."""
        return self.message_repo.get_messages_as_dicts(session_id)
