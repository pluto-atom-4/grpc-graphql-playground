"""Database session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings
from app.db.models import Base


def create_db_engine():
    """Create database engine based on configuration."""
    # SQLite for development: sqlite:///./recommender.db
    # PostgreSQL for production: postgresql://user:password@host/dbname
    connect_args = {}

    # SQLite specific arguments
    if "sqlite" in settings.database_url:
        connect_args = {"check_same_thread": False}

    engine = create_engine(
        settings.database_url,
        echo=settings.db_echo,
        connect_args=connect_args,
        pool_pre_ping=True,  # Test connections before using
    )
    return engine


# Global engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine (lazy initialization)."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def get_session_factory():
    """Get or create session factory (lazy initialization)."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


def init_db():
    """Initialize database schema (create all tables)."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Get a new database session."""
    SessionLocal = get_session_factory()
    return SessionLocal()


def close_session(session: Session):
    """Close a database session."""
    if session:
        session.close()
