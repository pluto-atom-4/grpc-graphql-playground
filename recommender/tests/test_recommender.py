"""Tests for the recommender service."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Base, Destination, UserEvent
from app.services.recommender import RecommenderService


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def recommender_service(db_session):
    """Create a recommender service with test database."""
    return RecommenderService(db_session)


@pytest.fixture
def test_destinations(db_session):
    """Add test destinations to database."""
    destinations = [
        Destination(
            id="dest_1",
            name="Paris",
            region="Île-de-France",
            country="France",
            popularity_score=0.9,
        ),
        Destination(
            id="dest_2",
            name="Tokyo",
            region="Kantō",
            country="Japan",
            popularity_score=0.8,
        ),
        Destination(
            id="dest_3",
            name="Barcelona",
            region="Catalonia",
            country="Spain",
            popularity_score=0.7,
        ),
    ]
    db_session.add_all(destinations)
    db_session.commit()
    return destinations


class TestRecommenderService:
    """Tests for RecommenderService."""

    def test_get_recommendations_empty_database(self, recommender_service):
        """Test getting recommendations from empty database."""
        recommendations = recommender_service.get_recommendations("user_1", limit=10)
        assert recommendations == []

    def test_get_recommendations_with_destinations(self, recommender_service, test_destinations):
        """Test getting recommendations with destinations available."""
        recommendations = recommender_service.get_recommendations("user_1", limit=10)

        # Should return all 3 destinations, ordered by popularity
        assert len(recommendations) == 3
        assert recommendations[0][0] == "dest_1"  # Highest popularity (0.9)
        assert recommendations[1][0] == "dest_2"  # Second (0.8)
        assert recommendations[2][0] == "dest_3"  # Third (0.7)

    def test_get_recommendations_respects_limit(self, recommender_service, test_destinations):
        """Test that limit parameter is respected."""
        recommendations = recommender_service.get_recommendations("user_1", limit=2)
        assert len(recommendations) == 2

    def test_get_recommendations_default_limit(self, recommender_service, test_destinations):
        """Test default limit is applied when limit <= 0."""
        recommendations = recommender_service.get_recommendations("user_1", limit=0)
        # Default limit is 10, we only have 3 destinations
        assert len(recommendations) == 3

    def test_process_event_records_event(self, recommender_service, test_destinations):
        """Test that events are recorded in database."""
        success = recommender_service.process_event(
            user_id="user_1",
            destination_id="dest_1",
            event_type="view",
        )

        assert success is True

        # Verify event was stored
        events = recommender_service.session.query(UserEvent).all()
        assert len(events) == 1
        assert events[0].user_id == "user_1"
        assert events[0].destination_id == "dest_1"
        assert events[0].event_type == "view"

    def test_process_event_updates_popularity(self, recommender_service, test_destinations):
        """Test that events update destination popularity."""
        original_score = test_destinations[0].popularity_score

        recommender_service.process_event(
            user_id="user_1",
            destination_id="dest_1",
            event_type="view",
        )

        # Refresh destination to get updated score
        updated_dest = recommender_service.session.query(Destination).filter_by(id="dest_1").first()
        assert updated_dest.popularity_score > original_score

    def test_process_event_with_rating(self, recommender_service, test_destinations):
        """Test processing event with rating."""
        success = recommender_service.process_event(
            user_id="user_1",
            destination_id="dest_1",
            event_type="rate",
            rating=5,
        )

        assert success is True

        events = recommender_service.session.query(UserEvent).all()
        assert len(events) == 1
        assert events[0].rating == 5

    def test_process_event_invalidates_cache(self, recommender_service, test_destinations):
        """Test that processing an event invalidates cached recommendations."""
        # Get recommendations first (should be cached)
        recommender_service.get_recommendations("user_1", limit=10)

        # Process an event
        recommender_service.process_event(
            user_id="user_1",
            destination_id="dest_1",
            event_type="view",
        )

        # Cache should be invalidated
        from app.db.models import Recommendation

        cached = recommender_service.session.query(Recommendation).filter_by(user_id="user_1").all()
        assert len(cached) == 0

    def test_ensure_default_destinations(self, db_session):
        """Test that default destinations are created."""
        service = RecommenderService(db_session)
        service.ensure_default_destinations()

        destinations = db_session.query(Destination).all()
        assert len(destinations) == 5  # Default 5 destinations
        assert any(d.name == "Paris" for d in destinations)
        assert any(d.name == "Tokyo" for d in destinations)

    def test_ensure_default_destinations_idempotent(self, db_session):
        """Test that ensure_default_destinations doesn't create duplicates."""
        service = RecommenderService(db_session)

        service.ensure_default_destinations()
        count_first = db_session.query(Destination).count()

        service.ensure_default_destinations()
        count_second = db_session.query(Destination).count()

        assert count_first == count_second == 5
