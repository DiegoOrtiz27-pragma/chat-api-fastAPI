"""
Defines the core Message entity for the domain layer.

This module contains the pure Python business object `Message`, its related
data structures, and the business logic for processing message content,
free of any external framework dependencies.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

# --- Custom Domain Exceptions ---

class InappropriateContentError(ValueError):
    """Custom exception raised when a message contains banned content."""
    def __init__(self, message: str = "El mensaje contiene contenido inapropiado."):
        self.message = message
        super().__init__(self.message)


# --- Domain Enums and Constants ---

class SenderType(str, Enum):
    """
    Enum for the sender of a message.
    """
    USER = "user"
    SYSTEM = "system"


BANNED_WORDS = {"palabraprohibida", "ofensivo", "inapropiado"}


# --- Domain Model (Pure Python Object) ---

class Message:
    """
    Represents a chat message entity.
    """
    def __init__(
        self,
        session_id: str,
        content: str,
        timestamp: datetime,
        sender: SenderType,
        message_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        if not content or not content.strip():
            raise ValueError("El contenido no puede estar vacío o solo ser un espacio en blanco.")

        self.message_id: UUID = message_id or uuid4()
        self.session_id: str = session_id
        self.content: str = content
        self.timestamp: datetime = timestamp
        self.sender: SenderType = sender
        self.metadata: dict[str, Any] = metadata or {}

    def process(self) -> None:
        """
        Executes the business logic for processing the message.

        Raises:
            InappropriateContentError: If the message content contains banned words.
        """
        self._filter_inappropriate_content()
        self._generate_metadata()

    def _filter_inappropriate_content(self) -> None:
        """Checks the message content against a list of banned words."""
        if any(word in self.content.lower() for word in BANNED_WORDS):
            raise InappropriateContentError()

    def _generate_metadata(self) -> None:
        """Calculates metadata and updates the 'metadata' attribute."""
        self.metadata["word_count"] = len(self.content.split())
        self.metadata["character_count"] = len(self.content)
        self.metadata["processed_at"] = datetime.now(timezone.utc).isoformat()