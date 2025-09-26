"""
Defines the API endpoints for message handling using FastAPI.

This module acts as the primary entrypoint for the application's API,
handling HTTP requests, validating data using Pydantic schemas, and
delegating business logic to the application service layer.
"""

from typing import List

from fastapi import APIRouter, Depends, status, Query, Path, Request, WebSocket, WebSocketDisconnect

from .dependencies import get_message_service, get_api_key, API_KEY
from .websocket_manager import manager

from src.application.services.message_service import MessageService
from src.domain.models.message import SenderType
from src.infrastructure.adapters.entrypoints.api.schemas import (
    MessageCreateRequest,
    MessageResponse,
    SuccessResponse,
)
from src.infrastructure.config.rate_limiter import limiter


# FastAPI router for all message-related endpoints
router = APIRouter(
    prefix="/api/messages",
    tags=["Messages"],
)


@router.post(
    "/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and Process a New Message",
    dependencies=[Depends(get_api_key)]
)
@limiter.limit("5/minute")
async def create_message(
    message_data: MessageCreateRequest,
    request: Request,
    service: MessageService = Depends(get_message_service)
):
    """
    Receives, processes, and stores a new chat message.

    - **Validates** the incoming message format.
    - **Processes** the message content for metadata and filtering.
    - **Stores** the message in the database.
    - **Returns** the processed message with metadata upon success.
    """
    
    processed_message = service.create_message(
        session_id=message_data.session_id,
        content=message_data.content,
        timestamp=message_data.timestamp,
        sender=message_data.sender
    )
    
    # Prepara mensaje para enviar por websocket
    response_for_ws = SuccessResponse(data=processed_message)
    
    # Envia mensaje a todos los clientes conectados
    await manager.broadcast(response_for_ws.model_dump_json())

    return response_for_ws

@router.get(
    "/{session_id}",
    response_model=List[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve Messages for a Session",
    dependencies=[Depends(get_api_key)]
)
@limiter.limit("5/minute")
def get_messages_by_session(
    request: Request,
    session_id: str = Path(..., description="The ID of the session to retrieve."),
    sender: SenderType | None = Query(
        default=None,
        description="Filter messages by sender ('user' or 'system')."
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of messages to return."
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of messages to skip for pagination."
    ),
    service: MessageService = Depends(get_message_service),
):
    """
    Retrieves a list of messages for a specific session, with support for
    pagination and filtering by sender.
    """
    messages = service.get_messages_for_session(
        session_id=session_id,
        sender=sender,
        limit=limit,
        offset=offset
    )
    
    return messages

@router.get(
    "/search/",
    response_model=List[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Search for Messages by Content",
    dependencies=[Depends(get_api_key)]
)
def search_messages(
    q: str = Query(..., min_length=3, description="The search term to find in message content."),
    service: MessageService = Depends(get_message_service),
):
    """
    Searches for messages across all sessions that contain the search term `q`.
    """
    messages = service.search_messages(query=q)
    return messages

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, api_key: str = Query(..., alias="X-API-Key")):
    """
    Endpoint for real-time message updates.
    Requires API key as a query parameter for authentication.
    """
    if api_key != API_KEY:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)