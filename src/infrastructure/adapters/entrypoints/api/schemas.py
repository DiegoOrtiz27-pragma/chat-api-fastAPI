"""
Defines the Pydantic schemas for API data validation and serialization.

These schemas act as the Data Transfer Objects (DTOs) for the API,
defining the expected structure for requests and the format for responses.
They are the boundary between the external world and the application's
entrypoint.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.domain.models.message import SenderType


# --- Schemas for Message Data ---

class MessageCreateRequest(BaseModel):
    """
    Schema for validating the payload of a new message creation request (POST).
    
    This model represents the data the client is expected to send.
    """
    session_id: str
    content: str = Field(..., min_length=1, description="Content cannot be empty.")
    timestamp: datetime
    sender: SenderType


class MessageMetadataResponse(BaseModel):
    """Schema for the nested metadata object in the response."""
    word_count: int
    character_count: int
    processed_at: datetime


class MessageResponse(BaseModel):
    """
    Schema for serializing a message object in an API response.
    
    This model defines the structure of the data sent back to the client.
    """
    message_id: UUID
    session_id: str
    content: str
    timestamp: datetime
    sender: SenderType
    metadata: MessageMetadataResponse

    # This configuration allows Pydantic to create this schema from an
    # arbitrary class object (like our pure domain 'Message' model),
    # accessing its attributes.
    model_config = ConfigDict(from_attributes=True)


# --- Schemas for Standardized API Responses ---

class SuccessResponse(BaseModel):
    """Generic success response wrapper."""
    status: str = "success"
    data: MessageResponse


class ErrorDetail(BaseModel):
    """Schema for the nested 'error' object."""
    code: str
    message: str
    details: str


class ErrorResponse(BaseModel):
    """
    Schema for a standardized error response.
    
    This matches the error format specified in the project requirements.
    """
    status: str = "error"
    error: ErrorDetail