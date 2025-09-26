"""
Concrete implementation of the IMessageRepository port using SQLAlchemy.

This module provides the adapter that connects the application's domain logic
to a relational database for message persistence.
"""

from typing import List
from sqlalchemy.orm import Session

from src.domain.models.message import Message, SenderType
from src.domain.ports.message_repository import IMessageRepository
from src.infrastructure.adapters.repositories.models.message_orm import MessageORM


class SQLiteMessageRepository(IMessageRepository):
    """
    A repository for persisting Message domain objects.

    This class adapts the domain's message entity to a relational database
    table, handling the mapping between the domain model and the ORM model.
    """

    def __init__(self, db_session: Session):
        """
        Initializes the repository with a database session.

        Args:
            db_session: An active SQLAlchemy Session for database operations.
        """
        self.db_session = db_session

    def save(self, message: Message) -> None:
        """
        Saves a Message domain object to the database.

        This method maps the domain object to its corresponding ORM model
        and commits it to the database session.

        Args:
            message: The Message domain object to persist.
        """
        
        message_orm = MessageORM(
            message_id=message.message_id,
            session_id=message.session_id,
            content=message.content,
            timestamp=message.timestamp,
            sender=message.sender,
            message_metadata=message.metadata
        )
        self.db_session.add(message_orm)
        self.db_session.commit()
        self.db_session.refresh(message_orm)

    def find_by_session_id(
        self,
        session_id: str,
        limit: int,
        offset: int,
        sender: SenderType | None = None,
    ) -> List[Message]:
        """
        Finds messages by session ID with optional filtering and pagination.

        Args:
            session_id: The ID of the session to search for.
            limit: The maximum number of results to return.
            offset: The number of results to skip.
            sender: Optional sender to filter results by.

        Returns:
            A list of Message domain objects.
        """
        query = self.db_session.query(MessageORM).filter(
            MessageORM.session_id == session_id
        )

        if sender:
            query = query.filter(MessageORM.sender == sender)

        results_orm = query.order_by(MessageORM.timestamp).offset(offset).limit(limit).all()

        return [
            Message(
                message_id=orm.message_id,
                session_id=orm.session_id,
                content=orm.content,
                timestamp=orm.timestamp,
                sender=orm.sender,
                metadata=orm.message_metadata
            )
            for orm in results_orm
        ]
    
    def search(self, query: str) -> List[Message]:
        """
        Performs a case-insensitive substring search on the message content.
        """
        results_orm = self.db_session.query(MessageORM).filter(
            MessageORM.content.ilike(f"%{query}%")
        ).all()

        return [
            Message(
                message_id=orm.message_id,
                session_id=orm.session_id,
                content=orm.content,
                timestamp=orm.timestamp,
                sender=orm.sender,
                metadata=orm.message_metadata
            )
            for orm in results_orm
        ]