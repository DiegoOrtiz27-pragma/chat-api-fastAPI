"""
Configures the database connection using SQLAlchemy.

This module sets up the engine, session factory, and declarative base
required for all database operations within the infrastructure layer.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL for SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./chat.db"

# SQLAlchemy Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base
Base = declarative_base()


def create_db_and_tables():
    """
    Utility function to create all database tables.

    This function should be called once when the application starts up
    to ensure the database schema is created based on the ORM models.
    """
    Base.metadata.create_all(bind=engine)