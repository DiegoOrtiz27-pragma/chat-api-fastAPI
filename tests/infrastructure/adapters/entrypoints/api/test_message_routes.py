"""
Integration tests for the API endpoints defined in message_routes.
"""
from typing import Iterator
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from datetime import datetime, timezone

from src.infrastructure.main import app
from src.application.services.message_service import MessageService
from src.domain.models.message import Message, SenderType
from src.infrastructure.adapters.entrypoints.api.dependencies import get_message_service, get_api_key
from src.infrastructure.adapters.entrypoints.api.websocket_manager import manager


@pytest.fixture
def mock_message_service() -> MagicMock:
    """Fixture to provide a clean mock MessageService for each test."""
    return MagicMock(spec=MessageService)


@pytest.fixture
def client(mock_message_service: MagicMock) -> Iterator[TestClient]:
    """
    Fixture to create a TestClient with all necessary dependencies overridden.
    """
    def override_get_api_key():
        return "clave-secreta-12345"

    app.dependency_overrides[get_message_service] = lambda: mock_message_service
    app.dependency_overrides[get_api_key] = override_get_api_key

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

# --- Helpers para crear mocks consistentes ---
def create_full_mock_message(session_id: str, content: str) -> Message:
    """Crea un objeto Message con metadata completa para los mocks."""
    msg = Message(
        session_id=session_id,
        content=content,
        timestamp=datetime.now(timezone.utc),
        sender=SenderType.USER
    )
    # LA ÚLTIMA CORRECCIÓN: Quitamos la "Z" extra del isoformat()
    msg.metadata = {
        "word_count": len(content.split()),
        "character_count": len(content),
        "processed_at": datetime.now(timezone.utc).isoformat()
    }
    return msg

# --- Pruebas Corregidas ---

def test_create_message_success(client: TestClient, mock_message_service: MagicMock):
    request_payload = {
        "session_id": "session-1",
        "content": "Test message",
        "timestamp": "2025-09-25T10:00:00Z",
        "sender": "user"
    }
    mock_processed_message = create_full_mock_message("session-1", "Test message")
    mock_message_service.create_message.return_value = mock_processed_message

    response = client.post(
        "/api/messages/",
        headers={"X-API-Key": "clave-secreta-12345"},
        json=request_payload
    )

    assert response.status_code == 201, f"Error: {response.text}"
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["data"]["content"] == "Test message"
    assert "word_count" in response_data["data"]["metadata"]

def test_create_message_validation_error(client: TestClient):
    invalid_payload = {"content": "Incomplete message"}
    response = client.post(
        "/api/messages/",
        headers={"X-API-Key": "clave-secreta-12345"},
        json=invalid_payload
    )
    assert response.status_code == 422

def test_get_messages_by_session_success(client: TestClient, mock_message_service: MagicMock):
    session_id = "session-to-find"
    mock_messages = [create_full_mock_message(session_id, "msg1")]
    mock_message_service.get_messages_for_session.return_value = mock_messages

    response = client.get(f"/api/messages/{session_id}", headers={"X-API-Key": "clave-secreta-12345"})

    assert response.status_code == 200, f"Error: {response.text}"
    assert len(response.json()) == 1
    assert "metadata" in response.json()[0]
    assert "word_count" in response.json()[0]["metadata"]

def test_search_messages_success(client: TestClient, mock_message_service: MagicMock):
    query = "findme"
    mock_messages = [create_full_mock_message("s1", "please findme")]
    mock_message_service.search_messages.return_value = mock_messages

    response = client.get(f"/api/messages/search/?q={query}", headers={"X-API-Key": "clave-secreta-12345"})

    assert response.status_code == 200, f"Error: {response.text}"
    assert len(response.json()) == 1
    assert "metadata" in response.json()[0]
    assert "character_count" in response.json()[0]["metadata"]

# --- Pruebas de WebSocket ---

def test_websocket_rejects_invalid_api_key(client: TestClient):
    invalid_key_url = "/api/messages/ws?X-API-Key=invalid-key"
    with pytest.raises(WebSocketDisconnect) as excinfo:
        with client.websocket_connect(invalid_key_url):
            pass
    assert excinfo.value.code == 1008

def test_websocket_connect_and_disconnect_success(client: TestClient):
    manager.active_connections.clear()
    valid_key_url = "/api/messages/ws?X-API-Key=clave-secreta-12345"
    assert len(manager.active_connections) == 0
    with client.websocket_connect(valid_key_url):
        assert len(manager.active_connections) == 1
    assert len(manager.active_connections) == 0

def test_websocket_receives_broadcast_message(client: TestClient, mock_message_service: MagicMock):
    manager.active_connections.clear()
    valid_key_url = "/api/messages/ws?X-API-Key=clave-secreta-12345"

    with client.websocket_connect(valid_key_url) as websocket:
        request_payload = {
            "session_id": "ws-session", "content": "broadcast this",
            "sender": "user", "timestamp": "2025-09-25T11:00:00Z"
        }
        mock_message = create_full_mock_message("ws-session", "broadcast this")
        mock_message_service.create_message.return_value = mock_message

        response = client.post(
            "/api/messages/",
            headers={"X-API-Key": "clave-secreta-12345"},
            json=request_payload
        )
        assert response.status_code == 201, f"Error en la respuesta: {response.text}"

        received_data = websocket.receive_json()

        assert received_data["status"] == "success"
        assert received_data["data"]["content"] == "broadcast this"
        assert "word_count" in received_data["data"]["metadata"]