import pytest

from app.repositories.session_repository import SessionRepository


class TestSessionRepository:
    def test_create_session(self, in_memory_db):
        repo = SessionRepository(in_memory_db)
        session = repo.create()
        assert session.id is not None
        assert session.title == "新对话"
        assert session.created_at is not None

    def test_create_session_with_custom_id(self, in_memory_db):
        repo = SessionRepository(in_memory_db)
        session = repo.create(session_id="custom-id", title="自定义")
        assert session.id == "custom-id"
        assert session.title == "自定义"

    def test_get_by_id(self, in_memory_db):
        repo = SessionRepository(in_memory_db)
        created = repo.create()
        found = repo.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id

    def test_get_by_id_not_found(self, in_memory_db):
        repo = SessionRepository(in_memory_db)
        assert repo.get_by_id("nonexistent") is None

    def test_list_all(self, in_memory_db):
        repo = SessionRepository(in_memory_db)
        repo.create()
        repo.create()
        sessions = repo.list_all()
        assert len(sessions) == 2

    def test_update_title(self, in_memory_db):
        repo = SessionRepository(in_memory_db)
        session = repo.create()
        updated = repo.update_title(session.id, "新标题")
        assert updated is not None
        assert updated.title == "新标题"

    def test_update_title_not_found(self, in_memory_db):
        repo = SessionRepository(in_memory_db)
        assert repo.update_title("nonexistent", "x") is None

    def test_delete_session(self, in_memory_db):
        repo = SessionRepository(in_memory_db)
        session = repo.create()
        assert repo.delete(session.id) is True
        assert repo.get_by_id(session.id) is None

    def test_delete_not_found(self, in_memory_db):
        repo = SessionRepository(in_memory_db)
        assert repo.delete("nonexistent") is False
