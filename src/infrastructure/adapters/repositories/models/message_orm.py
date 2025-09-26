"""
Defines the SQLAlchemy ORM model for a Message.

This module provides the database-specific mapping for the Message domain entity,
allowing it to be persisted in a relational database.
"""

from sqlalchemy import Column, String, DateTime, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.infrastructure.config.database import Base
from src.domain.models.message import SenderType


class MessageORM(Base):
    """SQLAlchemy model representing the 'messages' table."""
    __tablename__ = "messages"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, nullable=False, index=True)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    sender = Column(Enum(SenderType), nullable=False)
    message_metadata = Column(JSON, nullable=False, default={})