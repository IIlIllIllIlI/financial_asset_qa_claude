import uuid

from sqlalchemy.orm import Session

from app.database.models.chat_session import ChatSession
from app.utils.time import utc_now_iso


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, session_id: str | None = None, title: str = "新对话") -> ChatSession:
        now = utc_now_iso()
        session = ChatSession(
            id=session_id or str(uuid.uuid4()),
            title=title,
            created_at=now,
            updated_at=now,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, session_id: str) -> ChatSession | None:
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def list_all(self) -> list[ChatSession]:
        return (
            self.db.query(ChatSession)
            .order_by(ChatSession.updated_at.desc())
            .all()
        )

    def update_title(self, session_id: str, title: str) -> ChatSession | None:
        session = self.get_by_id(session_id)
        if session is None:
            return None
        session.title = title
        session.updated_at = utc_now_iso()
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_timestamp(self, session_id: str) -> None:
        session = self.get_by_id(session_id)
        if session:
            session.updated_at = utc_now_iso()
            self.db.commit()

    def delete(self, session_id: str) -> bool:
        session = self.get_by_id(session_id)
        if session is None:
            return False
        self.db.delete(session)
        self.db.commit()
        return True
