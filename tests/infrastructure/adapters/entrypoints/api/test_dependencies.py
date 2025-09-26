"""
Unit tests for the dependency injection providers.

These tests verify that each dependency provider function behaves correctly
in isolation. Dependencies to other providers or external systems are mocked.
"""
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, status

from src.infrastructure.adapters.entrypoints.api.dependencies import (
    get_api_key,
    get_db_session,
    get_message_repository,
    get_message_service,
    API_KEY,
)
from src.infrastructure.adapters.repositories.sqlite_message_repository import SQLiteMessageRepository
from src.application.services.message_service import MessageService
from src.domain.ports.message_repository import IMessageRepository


# --- Tests for get_api_key ---

@pytest.mark.asyncio
async def test_get_api_key_success():
    """Test Case: get_api_key returns the key when it is valid."""
    result = await get_api_key(API_KEY)
    assert result == API_KEY


@pytest.mark.asyncio
async def test_get_api_key_failure_invalid_key():
    """Test Case: get_api_key raises HTTPException for an invalid key."""
    with pytest.raises(HTTPException) as excinfo:
        await get_api_key("invalid-key")
    
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Clave API no válida" in excinfo.value.detail


# --- Tests for get_db_session ---

def test_get_db_session(mocker):
    """
    Test Case: get_db_session yields a session and closes it afterwards.
    We mock SessionLocal to avoid creating a real DB connection.
    """
    mock_session = MagicMock()
    mock_session_local = mocker.patch(
        "src.infrastructure.adapters.entrypoints.api.dependencies.SessionLocal",
        return_value=mock_session
    )

    db_generator = get_db_session()
    yielded_session = next(db_generator)

    assert yielded_session == mock_session
    mock_session_local.assert_called_once()
    
    mock_session.close.assert_not_called()

    with pytest.raises(StopIteration):
        next(db_generator)
    
    mock_session.close.assert_called_once()


# --- Tests for get_message_repository ---

def test_get_message_repository():
    """
    Test Case: get_message_repository creates and returns a SQLiteMessageRepository instance.
    """
    mock_session = MagicMock()
    
    repository = get_message_repository(mock_session)
    
    assert isinstance(repository, SQLiteMessageRepository)
    assert repository.db_session == mock_session


# --- Tests for get_message_service ---

def test_get_message_service():
    """
    Test Case: get_message_service creates and returns a MessageService instance.
    """
    mock_repository = MagicMock(spec=IMessageRepository)

    service = get_message_service(mock_repository)

    assert isinstance(service, MessageService)
    assert service.message_repo == mock_repository