from app.repositories.session_repository import SessionRepository
from app.repositories.message_repository import MessageRepository


class TestMessageRepository:
    def test_create_message(self, in_memory_db):
        session_repo = SessionRepository(in_memory_db)
        session = session_repo.create()

        msg_repo = MessageRepository(in_memory_db)
        msg = msg_repo.create(session.id, "user", "Hello")
        assert msg.id is not None
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.session_id == session.id

    def test_create_with_metadata(self, in_memory_db):
        session_repo = SessionRepository(in_memory_db)
        session = session_repo.create()

        msg_repo = MessageRepository(in_memory_db)
        msg = msg_repo.create(session.id, "assistant", "Response", {"key": "value"})
        assert msg.metadata_json is not None

    def test_get_by_session_id(self, in_memory_db):
        session_repo = SessionRepository(in_memory_db)
        session = session_repo.create()

        msg_repo = MessageRepository(in_memory_db)
        msg_repo.create(session.id, "user", "Q1")
        msg_repo.create(session.id, "assistant", "A1")

        messages = msg_repo.get_by_session_id(session.id)
        assert len(messages) == 2

    def test_get_messages_as_dicts(self, in_memory_db):
        session_repo = SessionRepository(in_memory_db)
        session = session_repo.create()

        msg_repo = MessageRepository(in_memory_db)
        msg_repo.create(session.id, "user", "Q1")

        dicts = msg_repo.get_messages_as_dicts(session.id)
        assert len(dicts) == 1
        assert dicts[0]["role"] == "user"
        assert dicts[0]["content"] == "Q1"

    def test_delete_by_session_id(self, in_memory_db):
        session_repo = SessionRepository(in_memory_db)
        session = session_repo.create()

        msg_repo = MessageRepository(in_memory_db)
        msg_repo.create(session.id, "user", "Q1")

        count = msg_repo.delete_by_session_id(session.id)
        assert count == 1
        assert len(msg_repo.get_by_session_id(session.id)) == 0
