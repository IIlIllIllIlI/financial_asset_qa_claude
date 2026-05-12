from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas.session import (
    SessionResponse,
    SessionDetailResponse,
    ChatMessageSchema,
    UpdateTitleRequest,
)
from app.database.session import get_db
from app.repositories.session_repository import SessionRepository
from app.repositories.message_repository import MessageRepository

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionResponse])
async def list_sessions(db: Session = Depends(get_db)):
    repo = SessionRepository(db)
    sessions = repo.list_all()
    return [
        SessionResponse(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in sessions
    ]


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(db: Session = Depends(get_db)):
    repo = SessionRepository(db)
    session = repo.create()
    return SessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    session_repo = SessionRepository(db)
    msg_repo = MessageRepository(db)

    session = session_repo.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = msg_repo.get_by_session_id(session_id)
    return SessionDetailResponse(
        session=SessionResponse(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
        ),
        messages=[
            ChatMessageSchema(
                id=m.id,
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )


@router.patch("/{session_id}/title", response_model=SessionResponse)
async def update_session_title(
    session_id: str,
    body: UpdateTitleRequest,
    db: Session = Depends(get_db),
):
    repo = SessionRepository(db)
    session = repo.update_title(session_id, body.title)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    msg_repo = MessageRepository(db)
    msg_repo.delete_by_session_id(session_id)

    session_repo = SessionRepository(db)
    deleted = session_repo.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
