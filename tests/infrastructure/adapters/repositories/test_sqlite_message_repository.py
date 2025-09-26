"""
Integration tests for the SQLiteMessageRepository.

These tests validate that the repository adapter correctly interacts with a
real database (an in-memory SQLite DB for testing) to perform CRUD
operations, ensuring that the mapping between domain and ORM models is correct.
"""
from typing import Iterator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timezone

from src.infrastructure.config.database import Base
from src.infrastructure.adapters.repositories.sqlite_message_repository import SQLiteMessageRepository
from src.domain.models.message import Message, SenderType

# --- Test Database Setup ---

@pytest.fixture(scope="function")
def db_session() -> Iterator[Session]:
    """
    Pytest fixture to create a new, clean in-memory database session for each test.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def message_repo(db_session: Session) -> SQLiteMessageRepository:
    """Fixture to provide a repository instance with the test session."""
    return SQLiteMessageRepository(db_session)


# --- Test Cases ---

def test_save_and_retrieve_message(db_session: Session, message_repo: SQLiteMessageRepository):
    """
    Test Case: A message can be saved and then retrieved.
    """
    message_to_save = Message(
        session_id="test-session-1",
        content="Hello, world!",
        timestamp=datetime.now(timezone.utc),
        sender=SenderType.USER,
    )

    message_repo.save(message_to_save)
    
    retrieved_messages = message_repo.find_by_session_id("test-session-1", 10, 0)
    assert len(retrieved_messages) == 1
    assert retrieved_messages[0].message_id == message_to_save.message_id
    assert retrieved_messages[0].content == "Hello, world!"


def test_find_by_session_id_with_filters(message_repo: SQLiteMessageRepository):
    """
    Test Case: find_by_session_id correctly filters by sender.
    """
    ts = datetime.now(timezone.utc)
    msg1 = Message("session-2", "user message", ts, SenderType.USER)
    msg2 = Message("session-2", "system message", ts, SenderType.SYSTEM)
    msg3 = Message("another-session", "another user message", ts, SenderType.USER)
    message_repo.save(msg1)
    message_repo.save(msg2)
    message_repo.save(msg3)

    user_messages = message_repo.find_by_session_id("session-2", 10, 0, sender=SenderType.USER)
    
    assert len(user_messages) == 1
    assert user_messages[0].content == "user message"


def test_find_by_session_id_pagination(message_repo: SQLiteMessageRepository):
    """
    Test Case: find_by_session_id correctly applies limit and offset.
    """
    ts = datetime.now(timezone.utc)
    for i in range(5):
        message_repo.save(Message("session-3", f"message {i}", ts, SenderType.USER))
    
    paginated_messages = message_repo.find_by_session_id("session-3", 2, 2)

    assert len(paginated_messages) == 2
    assert paginated_messages[0].content == "message 2"
    assert paginated_messages[1].content == "message 3"


def test_search_messages_case_insensitive(message_repo: SQLiteMessageRepository):
    """
    Test Case: search method finds content case-insensitively.
    """
    ts = datetime.now(timezone.utc)
    msg1 = Message("session-4", "This is a Test message.", ts, SenderType.USER)
    msg2 = Message("session-4", "Another message entirely.", ts, SenderType.SYSTEM)
    message_repo.save(msg1)
    message_repo.save(msg2)
    
    search_results = message_repo.search("test")
    
    assert len(search_results) == 1
    assert search_results[0].content == "This is a Test message."


def test_search_returns_empty_list_when_no_match(message_repo: SQLiteMessageRepository):
    """
    Test Case: search returns an empty list when no content matches.
    """
    ts = datetime.now(timezone.utc)
    message_repo.save(Message("session-5", "Some content here.", ts, SenderType.USER))
    
    search_results = message_repo.search("nonexistent")
    
    assert search_results == []