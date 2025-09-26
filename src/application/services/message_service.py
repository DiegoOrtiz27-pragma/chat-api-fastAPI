"""
Implements the application service for message-related use cases.

This module contains the MessageService class, which orchestrates the
application's core logic by coordinating domain models and repository ports.
It is completely independent of the web framework and database implementation.
"""

from datetime import datetime
from typing import List

from src.domain.models.message import Message, SenderType
from src.domain.ports.message_repository import IMessageRepository


class MessageService:
    """
    Provides application services for managing messages.

    This service implements the main use cases of the application, acting
    as an intermediary between the infrastructure (API endpoints) and the
    domain (business models and rules).
    """

    def __init__(self, message_repository: IMessageRepository):
        """
        Initializes the MessageService with a repository dependency.

        Args:
            message_repository: An object that conforms to the IMessageRepository interface for data persistence.
        """
        self.message_repo = message_repository

    def create_message(
        self,
        session_id: str,
        content: str,
        timestamp: datetime,
        sender: SenderType,
    ) -> Message:
        """
        Creates, processes, and stores a new message.

        This method orchestrates the creation of a message.

        Args:
            session_id: The identifier for the chat session.
            content: The text content of the message.
            timestamp: The time the message was originally sent.
            sender: The sender of the message ('user' or 'system').

        Returns:
            The processed Message domain object after it has been saved.

        Raises:
            InappropriateContentError: If the domain model detects banned content.
            ValueError: If the domain model validation fails (e.g., empty content).
        """

        message = Message(
            session_id=session_id,
            content=content,
            timestamp=timestamp,
            sender=sender
        )

        message.process()

        self.message_repo.save(message)

        return message

    def get_messages_for_session(
        self,
        session_id: str,
        limit: int,
        offset: int,
        sender: SenderType | None = None,
    ) -> List[Message]:
        """
        Retrieves all messages for a given session with pagination and filtering.

        This method acts as a pass-through to the repository port to query
        for messages based on the specified criteria.

        Args:
            session_id: The ID of the session to retrieve messages for.
            limit: The maximum number of messages to return.
            offset: The starting point for retrieving messages.
            sender: An optional filter to get messages from a specific sender.

        Returns:
            A list of Message domain objects that match the query.
        """
        return self.message_repo.find_by_session_id(
            session_id=session_id,
            limit=limit,
            offset=offset,
            sender=sender
        )
    
    def search_messages(self, query: str) -> List[Message]:
        """
        Searches for messages based on a content query.

        Args:
            query: The text to search for.

        Returns:
            A list of matching Message domain objects.
        """
        return self.message_repo.search(query)