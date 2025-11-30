"""Database configuration and session management.

Creates SQLModel engine and session factory for PostgreSQL database.
"""
# database.py
# (1) Create SQLModel engine and session factory, and helper to create tables.

import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv(dotenv_path=".env")  # load .env when running backend

DB_USER = os.getenv("POSTGRES_USER", "pias123")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pias123")
DB_NAME = os.getenv("POSTGRES_DB", "pias_db")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")                                                                       
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)  # set echo=True to see SQL logs

def create_db_and_tables():
    """Create DB tables from SQLModel models (call on startup)."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Yield a DB session — use as a dependency in FastAPI."""
    with Session(engine) as session:
        yield session
