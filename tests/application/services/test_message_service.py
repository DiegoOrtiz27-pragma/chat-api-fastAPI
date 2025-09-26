"""
Unit tests for the MessageService.

These tests verify the application service's logic in isolation by mocking
its dependencies (e.g., the repository). This ensures that the service
correctly orchestrates the domain models and repository interactions.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.application.services.message_service import MessageService
from src.domain.models.message import Message, SenderType, InappropriateContentError
from src.domain.ports.message_repository import IMessageRepository


@pytest.fixture
def mock_repo() -> MagicMock:
    """Provides a MagicMock object simulating the IMessageRepository."""
    return MagicMock(spec=IMessageRepository)


@pytest.fixture
def message_service(mock_repo: MagicMock) -> MessageService:
    """Provides an instance of MessageService with a mocked repository."""
    return MessageService(message_repository=mock_repo)


def test_create_message_success(message_service: MessageService, mock_repo: MagicMock):
    """
    Test Case: create_message successfully processes and saves a valid message.
    """
    
    message_data = {
        "session_id": "session-1",
        "content": "A valid message.",
        "timestamp": datetime.now(timezone.utc),
        "sender": SenderType.USER,
    }

    result_message = message_service.create_message(**message_data)

    mock_repo.save.assert_called_once()
    
    saved_message_arg = mock_repo.save.call_args[0][0]
    assert isinstance(saved_message_arg, Message)
    assert "word_count" in saved_message_arg.metadata
    
    assert "word_count" in result_message.metadata
    assert result_message.content == message_data["content"]


def test_create_message_fails_on_inappropriate_content(
    message_service: MessageService, mock_repo: MagicMock
):
    """
    Test Case: create_message raises an error and does NOT save the message
    if the content is inappropriate.
    """
    
    message_data = {
        "session_id": "session-2",
        "content": "This is an ofensivo message.",
        "timestamp": datetime.now(timezone.utc),
        "sender": SenderType.USER,
    }

    with pytest.raises(InappropriateContentError):
        message_service.create_message(**message_data)

    mock_repo.save.assert_not_called()


def test_get_messages_for_session(message_service: MessageService, mock_repo: MagicMock):
    """
    Test Case: get_messages_for_session correctly calls the repository and returns its result.
    """
    session_id = "session-3"
    fake_messages = [Message(session_id=session_id, content="msg1", timestamp=datetime.now(timezone.utc), sender=SenderType.USER)]
    mock_repo.find_by_session_id.return_value = fake_messages

    result = message_service.get_messages_for_session(
        session_id=session_id, limit=10, offset=0, sender=None
    )

    mock_repo.find_by_session_id.assert_called_once_with(
        session_id=session_id, limit=10, offset=0, sender=None
    )
    
    assert result == fake_messages


def test_search_messages(message_service: MessageService, mock_repo: MagicMock):
    """
    Test Case: search_messages correctly calls the repository and returns its result.
    """
    
    query = "test"
    fake_messages = [Message(session_id="search-session", content="A test message", timestamp=datetime.now(timezone.utc), sender=SenderType.USER)]
    mock_repo.search.return_value = fake_messages
    
    result = message_service.search_messages(query=query)
    
    mock_repo.search.assert_called_once_with(query)
    assert result == fake_messages