"""
Main entrypoint for the FastAPI application.
"""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Infrastructure imports
from src.infrastructure.config.database import create_db_and_tables
from src.infrastructure.config.rate_limiter import limiter
from src.infrastructure.adapters.entrypoints.api import message_routes
from src.infrastructure.adapters.entrypoints.api.error_handlers import (
    validation_exception_handler,
    business_logic_exception_handler,
    generic_exception_handler,
)

# Application and Domain imports
from src.domain.models.message import InappropriateContentError

# --- Application Factory ---

def create_app() -> FastAPI:
    create_db_and_tables()

    app = FastAPI(
        title="Chat Message Processing API",
        description="A RESTful API for processing chat messages.",
        version="1.0.0"
    )
    
    # --- Set limiter ---
    app.state.limiter = limiter
     
    # --- Register Centralized Exception Handlers ---
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValueError, business_logic_exception_handler)
    app.add_exception_handler(InappropriateContentError, business_logic_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # --- Add middleware
    app.add_middleware(SlowAPIMiddleware)
    
    # --- Include the API Router ---
    app.include_router(message_routes.router)

    return app

# Create the final application instance
app = create_app()