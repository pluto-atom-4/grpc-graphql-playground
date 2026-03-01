"""Database models for the recommender service."""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Destination(Base):
    """Travel destination model."""

    __tablename__ = "destinations"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    region = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    description = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    popularity_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Destination(id={self.id}, name={self.name}, country={self.country})>"


class UserEvent(Base):
    """User interaction event model."""

    __tablename__ = "user_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    destination_id = Column(String(50), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # "view", "click", "book", "rate"
    rating = Column(Integer)  # 1-5 star rating, optional
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<UserEvent(user={self.user_id}, dest={self.destination_id}, type={self.event_type})>"


class UserPreference(Base):
    """Aggregated user preference model (built from events)."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, unique=True, index=True)
    preferred_regions = Column(Text)  # JSON-encoded list of regions
    preferred_countries = Column(Text)  # JSON-encoded list of countries
    event_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<UserPreference(user_id={self.user_id}, events={self.event_count})>"


class Recommendation(Base):
    """Cached recommendation model."""

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    destination_id = Column(String(50), nullable=False, index=True)
    score = Column(Float, nullable=False)  # 0.0 to 1.0
    rank = Column(Integer)  # Position in recommendations list
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)  # TTL for cache invalidation

    def __repr__(self) -> str:
        return f"<Recommendation(user={self.user_id}, dest={self.destination_id}, score={self.score})>"
