"""
Defines the data persistence port for the domain layer.

This module specifies the contract that any storage
adapter must implement for handling Message entities. It ensures that the
application's core logic remains independent of the database technology.
"""

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from src.domain.models.message import Message, SenderType


class IMessageRepository(ABC):
    """
    An abstract interface for a message repository.

    This class defines the standard operations that must be supported by any
    concrete repository implementation for Message objects.
    """

    @abstractmethod
    def save(self, message: Message) -> None:
        """
        Persists a Message object to the data store.

        Args:
            message: The Message domain object to be saved.
        
        Raises:
            Exception: Implementation-specific errors during data persistence.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_session_id(
        self,
        session_id: str,
        limit: int,
        offset: int,
        sender: SenderType | None = None,
    ) -> List[Message]:
        """
        Retrieves a list of messages for a given session, with support for
        pagination and filtering.

        Args:
            session_id: The ID of the session to retrieve messages for.
            limit: The maximum number of messages to return (for pagination).
            offset: The starting point for retrieving messages (for pagination).
            sender: An optional filter to retrieve messages only from a
                    specific sender ('user' or 'system').

        Returns:
            A list of Message domain objects matching the criteria.
        """
        raise NotImplementedError
    
    @abstractmethod 
    def search(self, query: str) -> List[Message]:
        """
        Searches for messages containing a specific text query.

        Args:
            query: The text string to search for in message content.

        Returns:
            A list of Message domain objects matching the search query.
        """
        raise NotImplementedError