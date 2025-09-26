"""
Unit tests for the Message domain model.

These tests verify the behavior of the Message class in complete isolation,
ensuring that its business rules, validation, and processing logic work
as expected without any external dependencies.
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID

from src.domain.models.message import (
    Message,
    SenderType,
    InappropriateContentError
)


@pytest.fixture
def valid_message_data() -> dict:
    """Provides a dictionary with valid data to create a Message instance."""
    return {
        "session_id": "session-123",
        "content": "Este es un mensaje de prueba.",
        "timestamp": datetime.now(timezone.utc),
        "sender": SenderType.USER,
    }


def test_message_creation_successful(valid_message_data):
    """
    Test Case: A Message can be created successfully with valid data.
    """
    # Arrange & Act
    message = Message(**valid_message_data)

    # Assert
    assert isinstance(message.message_id, UUID)
    assert message.session_id == valid_message_data["session_id"]
    assert message.content == valid_message_data["content"]
    assert message.timestamp == valid_message_data["timestamp"]
    assert message.sender == valid_message_data["sender"]
    assert message.metadata == {}


@pytest.mark.parametrize(
    "invalid_content",
    ["", "   ", "\n \t"]
)
def test_message_creation_fails_with_invalid_content(invalid_content, valid_message_data):
    """
    Test Case: Message creation fails if content is empty or only whitespace.
    """
    # Arrange
    valid_message_data["content"] = invalid_content

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        Message(**valid_message_data)
    assert "El contenido no puede estar vacío" in str(excinfo.value)


def test_process_adds_correct_metadata(valid_message_data):
    """
    Test Case: The process() method correctly calculates and adds metadata.
    """
    # Arrange
    message = Message(**valid_message_data)
    expected_word_count = len(valid_message_data["content"].split())
    expected_char_count = len(valid_message_data["content"])

    # Act
    message.process()

    # Assert
    assert "word_count" in message.metadata
    assert "character_count" in message.metadata
    assert "processed_at" in message.metadata
    assert message.metadata["word_count"] == expected_word_count
    assert message.metadata["character_count"] == expected_char_count
    assert isinstance(message.metadata["processed_at"], str)


def test_process_fails_with_inappropriate_content(valid_message_data):
    """
    Test Case: The process() method raises InappropriateContentError for banned words.
    """
    # Arrange
    valid_message_data["content"] = "Este es un mensaje ofensivo."
    message = Message(**valid_message_data)

    # Act & Assert
    with pytest.raises(InappropriateContentError) as excinfo:
        message.process()

    assert "contenido inapropiado" in str(excinfo.value)
    # Verify that metadata was not generated because the process failed
    assert message.metadata == {}


def test_filter_is_case_insensitive(valid_message_data):
    """
    Test Case: The inappropriate content filter is case-insensitive.
    """
    # Arrange
    valid_message_data["content"] = "Este es un mensaje OFENSIVO."
    message = Message(**valid_message_data)

    # Act & Assert
    with pytest.raises(InappropriateContentError):
        message.process()