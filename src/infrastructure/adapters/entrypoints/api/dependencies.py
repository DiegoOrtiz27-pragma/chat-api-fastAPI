"""
Defines dependency injection providers for the API layer.
"""
from typing import Iterator
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader 

from src.infrastructure.config.database import SessionLocal
from src.infrastructure.adapters.repositories.sqlite_message_repository import SQLiteMessageRepository
from src.application.services.message_service import MessageService
from src.domain.ports.message_repository import IMessageRepository

API_KEY = "clave-secreta-12345"
API_KEY_NAME = "X-API-Key"

api_key_header_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# --- Security ---

async def get_api_key(api_key: str = Security(api_key_header_scheme)):
    """
    Dependency to validate the API Key from the request header.
    """
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave API no válida o faltante"
        )


# --- Dependency Injection Providers ---

def get_db_session() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_message_repository(db: Session = Depends(get_db_session)) -> IMessageRepository:
    return SQLiteMessageRepository(db)


def get_message_service(repo: IMessageRepository = Depends(get_message_repository)) -> MessageService:
    return MessageService(repo)