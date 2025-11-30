"""Database configuration and session management.

Creates SQLModel engine and session factory for PostgreSQL database.
Includes connection validation and error handling.
"""
# database.py
# (1) Create SQLModel engine and session factory, and helper to create tables.

import os
import sys
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import OperationalError

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

DB_USER = os.getenv("POSTGRES_USER", "pias123")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pias123")
DB_NAME = os.getenv("POSTGRES_DB", "pias_db")
DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
SQLITE_URL = os.getenv("SQLITE_URL", "sqlite:///./app.db")

# Create SQLAlchemy engine
# echo=False: Disable SQL query logging (set to True for debugging)
# pool_pre_ping=True: Test connections before using them from the pool
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)


def create_db_and_tables() -> None:
    """Create database tables from SQLModel models.
    
    Should be called on application startup to ensure all tables exist.
    Creates tables if they don't exist, but doesn't modify existing ones.
    
    Raises:
        OperationalError: If unable to connect to the database
    """
    global engine
    try:
        SQLModel.metadata.create_all(engine)
        print("✅ Database tables created/verified successfully")
    except OperationalError as e:
        print(f"❌ Failed to connect to database: {e}")
        print(f"   Database URL: postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        print("   Falling back to SQLite for development")
        try:
            engine = create_engine(
                SQLITE_URL,
                echo=False,
                connect_args={"check_same_thread": False}
            )
            SQLModel.metadata.create_all(engine)
            print("✅ SQLite fallback initialized successfully")
        except Exception as e2:
            print(f"❌ Fallback to SQLite failed: {e2}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error creating database tables: {e}")
        sys.exit(1)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for dependency injection in FastAPI.
    
    This function is used as a FastAPI dependency to provide database sessions
    to route handlers. The session is automatically closed after the request.
    
    Usage:
        @app.get("/endpoint")
        def endpoint(session: Session = Depends(get_session)):
            # Use session here
            pass
    
    Yields:
        Session: SQLModel/SQLAlchemy database session
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


def test_connection() -> bool:
    """Test database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with Session(engine) as session:
            session.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False
