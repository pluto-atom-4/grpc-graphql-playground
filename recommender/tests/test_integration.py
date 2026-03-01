"""Integration tests for full stack services."""

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Base, Destination, UserEvent, Recommendation
from app.services.recommender import RecommenderService


@pytest.fixture
def db_session():
    """Create an in-memory test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session

    session.close()


class TestIntegrationFlow:
    """Integration tests for the full recommendation flow."""

    def test_event_flow_updates_recommendations(self, db_session):
        """Test: Event → Processed → Affects Recommendations."""
        # Setup: Create destinations
        destinations = [
            Destination(
                id="paris_001",
                name="Paris",
                region="Île-de-France",
                country="France",
                popularity_score=0.5,
            ),
            Destination(
                id="tokyo_001",
                name="Tokyo",
                region="Kantō",
                country="Japan",
                popularity_score=0.5,
            ),
        ]
        db_session.add_all(destinations)
        db_session.commit()

        service = RecommenderService(db_session)

        # Initial state: both have equal popularity
        initial_recs = service.get_recommendations("user_1", 10)
        assert len(initial_recs) == 2
        initial_scores = {rec[0]: rec[1] for rec in initial_recs}

        # Record an event for Paris
        service.process_event("user_1", "paris_001", "view")

        # Verify: Paris popularity increased
        updated_recs = service.get_recommendations("user_1", 10)
        updated_scores = {rec[0]: rec[1] for rec in updated_recs}

        assert updated_scores["paris_001"] > initial_scores["paris_001"]

    def test_user_events_persisted(self, db_session):
        """Test: User events are persisted to database."""
        # Setup
        dest = Destination(
            id="dest_1",
            name="Test Destination",
            region="Test",
            country="Test",
            popularity_score=0.5,
        )
        db_session.add(dest)
        db_session.commit()

        service = RecommenderService(db_session)

        # Record multiple events
        events = [
            ("user_1", "dest_1", "view"),
            ("user_1", "dest_1", "click"),
            ("user_2", "dest_1", "view"),
        ]

        for user_id, dest_id, event_type in events:
            service.process_event(user_id, dest_id, event_type)

        # Verify: All events are persisted
        all_events = db_session.query(UserEvent).all()
        assert len(all_events) >= len(events)

    def test_recommendations_cache_invalidation(self, db_session):
        """Test: Recommendations are cached and invalidated on event."""
        dest = Destination(
            id="dest_1",
            name="Test",
            region="Test",
            country="Test",
            popularity_score=0.5,
        )
        db_session.add(dest)
        db_session.commit()

        service = RecommenderService(db_session)

        # Get recommendations (caches them)
        recs_1 = service.get_recommendations("user_1", 10)
        assert len(recs_1) > 0

        # Verify cache exists
        cached = db_session.query(Recommendation).filter_by(user_id="user_1").all()
        assert len(cached) > 0

        # Process event
        service.process_event("user_1", "dest_1", "view")

        # Verify: Cache was invalidated
        cached_after = (
            db_session.query(Recommendation).filter_by(user_id="user_1").all()
        )
        assert len(cached_after) == 0

    def test_multiple_users_independent(self, db_session):
        """Test: Recommendations for different users are independent."""
        destinations = [
            Destination(
                id="dest_1",
                name="Destination 1",
                region="Region 1",
                country="Country 1",
                popularity_score=0.5,
            ),
            Destination(
                id="dest_2",
                name="Destination 2",
                region="Region 2",
                country="Country 2",
                popularity_score=0.5,
            ),
        ]
        db_session.add_all(destinations)
        db_session.commit()

        service = RecommenderService(db_session)

        # User 1: Interacts with dest_1
        service.process_event("user_1", "dest_1", "view")

        # User 2: Gets initial recommendations (no interactions)
        recs_user_2 = service.get_recommendations("user_2", 10)
        assert len(recs_user_2) == 2

        # Verify both destinations still have similar scores for user_2
        scores = [r[1] for r in recs_user_2]
        # (They won't be exactly equal due to the view event affecting popularity)
        assert max(scores) - min(scores) < 0.2

    def test_event_with_rating(self, db_session):
        """Test: Event with rating is processed correctly."""
        dest = Destination(
            id="dest_1",
            name="Test",
            region="Test",
            country="Test",
            popularity_score=0.5,
        )
        db_session.add(dest)
        db_session.commit()

        service = RecommenderService(db_session)

        # Record event with high rating
        service.process_event("user_1", "dest_1", "rate", rating=5)

        # Verify event was stored with rating
        event = db_session.query(UserEvent).first()
        assert event is not None
        assert event.rating == 5
        assert event.event_type == "rate"

    def test_default_destinations_created(self, db_session):
        """Test: Default destinations are automatically created."""
        service = RecommenderService(db_session)

        # Verify no destinations yet
        existing = db_session.query(Destination).count()
        assert existing == 0

        # Create defaults
        service.ensure_default_destinations()

        # Verify defaults were created
        defaults = db_session.query(Destination).all()
        assert len(defaults) == 5

        # Verify specific destinations exist
        names = {d.name for d in defaults}
        assert "Paris" in names
        assert "Tokyo" in names
        assert "Barcelona" in names
