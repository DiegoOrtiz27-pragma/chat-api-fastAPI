"""
Unit tests for the centralized API exception handlers.

These tests ensure that each handler correctly catches its target exception
and formats the error into the standardized JSON response required by the API contract.
"""
import pytest
import json
from unittest.mock import MagicMock

from fastapi.exceptions import RequestValidationError

from src.domain.models.message import InappropriateContentError
from src.infrastructure.adapters.entrypoints.api.error_handlers import (
    validation_exception_handler,
    business_logic_exception_handler,
    generic_exception_handler,
)

# --- Tests for validation_exception_handler ---

@pytest.mark.asyncio
async def test_validation_exception_handler_for_missing_field():
    """
    Test Case: The handler correctly formats a 'missing' validation error.
    """
    mock_request = MagicMock()
    pydantic_errors = [{"loc": ("body", "session_id"), "type": "missing"}]
    exception = RequestValidationError(errors=pydantic_errors)

    response = await validation_exception_handler(mock_request, exception)
    response_body = json.loads(response.body.decode())

    assert response.status_code == 422
    assert response_body["error"]["code"] == "INVALID_FORMAT"
    assert response_body["error"]["details"] == "El campo 'session_id' es requerido."


@pytest.mark.asyncio
async def test_validation_exception_handler_for_enum_error():
    """
    Test Case: The handler correctly formats an 'enum' validation error.
    """
    mock_request = MagicMock()
    pydantic_errors = [{"loc": ("body", "sender"), "type": "enum"}]
    exception = RequestValidationError(errors=pydantic_errors)

    response = await validation_exception_handler(mock_request, exception)
    response_body = json.loads(response.body.decode())

    assert response.status_code == 422
    assert response_body["error"]["code"] == "INVALID_FORMAT"
    assert "debe ser uno de los valores permitidos" in response_body["error"]["details"]


# --- Tests for business_logic_exception_handler ---

@pytest.mark.asyncio
async def test_business_logic_exception_handler_for_inappropriate_content():
    """
    Test Case: The handler correctly formats an InappropriateContentError.
    """
    mock_request = MagicMock()
    exception = InappropriateContentError("Contenido ofensivo detectado.")

    response = await business_logic_exception_handler(mock_request, exception)
    response_body = json.loads(response.body.decode())
    
    assert response.status_code == 400
    assert response_body["error"]["code"] == "BUSINESS_RULE_VIOLATION"
    assert response_body["error"]["details"] == "Contenido ofensivo detectado."


@pytest.mark.asyncio
async def test_business_logic_exception_handler_for_value_error():
    """
    Test Case: The handler correctly formats a generic ValueError.
    """
    mock_request = MagicMock()
    exception = ValueError("El contenido no puede estar vacío.")

    response = await business_logic_exception_handler(mock_request, exception)
    response_body = json.loads(response.body.decode())

    assert response.status_code == 400
    assert response_body["error"]["code"] == "BUSINESS_RULE_VIOLATION"
    assert response_body["error"]["details"] == "El contenido no puede estar vacío."


# --- Tests for generic_exception_handler ---

@pytest.mark.asyncio
async def test_generic_exception_handler():
    """
    Test Case: The handler correctly formats an unexpected generic Exception.
    """
    mock_request = MagicMock()
    exception = Exception("Un error inesperado del servidor.")

    response = await generic_exception_handler(mock_request, exception)
    response_body = json.loads(response.body.decode())

    assert response.status_code == 500
    assert response_body["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "Se ha registrado el error" in response_body["error"]["details"]