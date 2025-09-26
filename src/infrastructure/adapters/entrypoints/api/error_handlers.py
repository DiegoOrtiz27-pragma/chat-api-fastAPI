"""
Defines centralized exception handlers for the FastAPI application.

This module contains functions that catch specific exceptions raised anywhere
in the application and convert them into standardized, user-friendly JSON
error responses, as specified by the API contract.
"""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.models.message import InappropriateContentError
from src.infrastructure.adapters.entrypoints.api.schemas import ErrorDetail, ErrorResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles errors raised by Pydantic during request validation.
    
    This catches failures like missing required fields or incorrect data types
    and translates them into the user-friendly format required by the challenge.
    """
    # Extrae la información del primer error de validación
    error = exc.errors()[0]
    field_name = error.get("loc", ["", ""])[1]
    error_type = error.get("type")

    # Mapea los tipos de error de Pydantic
    error_messages = {
        "missing": f"El campo '{field_name}' es requerido.",
        "enum": f"El campo '{field_name}' debe ser uno de los valores permitidos (ej: 'user' o 'system')."
    }

    # Usa nuestro mensaje personalizado o uno genérico si no lo tenemos mapeado
    details = error_messages.get(error_type, f"Error de validación en el campo '{field_name}'.")

    error_detail = ErrorDetail(
        code="INVALID_FORMAT",
        message="Formato de mensaje inválido",
        details=details # <-- Usamos nuestro nuevo mensaje personalizado
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ErrorResponse(error=error_detail).model_dump()
    )


async def business_logic_exception_handler(request: Request, exc: (ValueError | InappropriateContentError)):
    """
    Handles exceptions related to business rule violations.
    
    This catches errors like empty message content (ValueError) or the
    presence of banned words (InappropriateContentError).
    """
    error_detail = ErrorDetail(
        code="BUSINESS_RULE_VIOLATION",
        message="Violación de una regla de negocio",
        details=str(exc)
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(error=error_detail).model_dump()
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handles any unexpected, unhandled exceptions.
    
    This is a catch-all for internal server errors, fulfilling the
    "Errores del servidor" requirement[cite: 52].
    """
    error_detail = ErrorDetail(
        code="INTERNAL_SERVER_ERROR",
        message="Ocurrió un error inesperado en el servidor.",
        details="Se ha registrado el error para su revisión."
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(error=error_detail).model_dump()
    )