"""Recommendation service logic."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.db.models import Destination, Recommendation, UserEvent, UserPreference


class RecommenderService:
    """Service for generating travel recommendations."""

    def __init__(self, session: Session):
        """Initialize recommender service with database session."""
        self.session = session

    def get_recommendations(self, user_id: str, limit: int = 10) -> list[tuple[str, float]]:
        """
        Generate personalized recommendations for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of recommendations to return

        Returns:
            List of (destination_id, score) tuples ordered by score
        """
        if limit <= 0:
            limit = 10

        # Check for cached recommendations
        cached = self._get_cached_recommendations(user_id, limit)
        if cached:
            return cached

        # Generate new recommendations using simple popularity algorithm
        recommendations = self._generate_recommendations(user_id, limit)

        # Cache the recommendations
        if recommendations:
            self._cache_recommendations(user_id, recommendations)

        return recommendations

    def _get_cached_recommendations(
        self, user_id: str, limit: int
    ) -> Optional[list[tuple[str, float]]]:
        """Retrieve cached recommendations if available and not expired."""
        cached = (
            self.session.query(Recommendation)
            .filter(
                and_(
                    Recommendation.user_id == user_id,
                    Recommendation.expires_at > datetime.utcnow(),
                )
            )
            .order_by(Recommendation.rank)
            .limit(limit)
            .all()
        )

        if cached:
            return [(rec.destination_id, rec.score) for rec in cached]
        return None

    def _generate_recommendations(self, user_id: str, limit: int) -> list[tuple[str, float]]:
        """Generate recommendations using popularity-based algorithm."""
        # MVP: Return top destinations by popularity score
        # Future: Use user event history, collaborative filtering, etc.

        destinations = (
            self.session.query(Destination)
            .order_by(desc(Destination.popularity_score))
            .limit(limit)
            .all()
        )

        return [
            (dest.id, min(dest.popularity_score, 1.0)) for dest in destinations
        ]  # Cap score at 1.0

    def _cache_recommendations(
        self, user_id: str, recommendations: list[tuple[str, float]]
    ) -> None:
        """Cache recommendations in database with TTL."""
        # Clear old cached recommendations
        self.session.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).delete()

        # Add new cached recommendations (24-hour TTL)
        ttl = datetime.utcnow() + timedelta(hours=24)
        for rank, (dest_id, score) in enumerate(recommendations, start=1):
            rec = Recommendation(
                user_id=user_id,
                destination_id=dest_id,
                score=score,
                rank=rank,
                expires_at=ttl,
            )
            self.session.add(rec)

        self.session.commit()

    def process_event(
        self,
        user_id: str,
        destination_id: str,
        event_type: str,
        rating: Optional[int] = None,
    ) -> bool:
        """
        Process a user event and update recommendation state.

        Args:
            user_id: User identifier
            destination_id: Destination identifier
            event_type: Type of event ("view", "click", "book", "rate")
            rating: Optional rating (1-5) for "rate" events

        Returns:
            True if event was processed successfully
        """
        try:
            # Record the event
            event = UserEvent(
                user_id=user_id,
                destination_id=destination_id,
                event_type=event_type,
                rating=rating,
            )
            self.session.add(event)

            # Update destination popularity based on event type
            self._update_destination_popularity(destination_id, event_type, rating)

            # Invalidate user's cached recommendations
            self.session.query(Recommendation).filter(
                Recommendation.user_id == user_id
            ).delete()

            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            print(f"Error processing event: {e}")
            return False

    def _update_destination_popularity(
        self, destination_id: str, event_type: str, rating: Optional[int] = None
    ) -> None:
        """Update destination popularity score based on event."""
        dest = self.session.query(Destination).filter(Destination.id == destination_id).first()

        if not dest:
            return

        # Simple scoring: different weights for event types
        score_delta = {
            "view": 0.01,
            "click": 0.05,
            "book": 0.20,
            "rate": 0.10 + (rating / 50.0 if rating else 0),  # Up to +0.10 for 5-star
        }.get(event_type, 0.01)

        dest.popularity_score = min(dest.popularity_score + score_delta, 1.0)
        self.session.flush()  # Update in session without committing yet

    def ensure_default_destinations(self) -> None:
        """Ensure default destination data exists in database."""
        # Check if destinations already exist
        if self.session.query(Destination).count() > 0:
            return

        default_destinations = [
            Destination(
                id="paris_001",
                name="Paris",
                region="Île-de-France",
                country="France",
                description="City of Light, famous for Eiffel Tower, museums, and cuisine",
                latitude=48.8566,
                longitude=2.3522,
                popularity_score=0.85,
            ),
            Destination(
                id="tokyo_001",
                name="Tokyo",
                region="Kantō",
                country="Japan",
                description="Vibrant metropolis with temples, gardens, and modern districts",
                latitude=35.6762,
                longitude=139.6503,
                popularity_score=0.80,
            ),
            Destination(
                id="barcelona_001",
                name="Barcelona",
                region="Catalonia",
                country="Spain",
                description="Mediterranean coastal city known for architecture and beaches",
                latitude=41.3851,
                longitude=2.1734,
                popularity_score=0.75,
            ),
            Destination(
                id="newyork_001",
                name="New York",
                region="New York",
                country="United States",
                description="The city that never sleeps, iconic landmarks and diverse culture",
                latitude=40.7128,
                longitude=-74.0060,
                popularity_score=0.82,
            ),
            Destination(
                id="sydney_001",
                name="Sydney",
                region="New South Wales",
                country="Australia",
                description="Stunning harbor city with Opera House and beautiful beaches",
                latitude=-33.8688,
                longitude=151.2093,
                popularity_score=0.78,
            ),
        ]

        self.session.add_all(default_destinations)
        self.session.commit()
