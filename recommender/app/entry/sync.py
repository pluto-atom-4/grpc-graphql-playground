"""Kafka consumer event loop for processing user events."""

import json
import logging
import sys
import time
from typing import Any, Dict

from kafka import KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from app.config.settings import settings
from app.db.session import get_session, init_db
from app.services.recommender import RecommenderService


# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class EventConsumer:
    """Kafka consumer for user events."""

    def __init__(self):
        """Initialize the event consumer."""
        self.consumer = None
        self.running = False

    def connect(self) -> None:
        """Connect to Kafka broker."""
        logger.info(f"Connecting to Kafka brokers: {settings.kafka_brokers}")

        try:
            self.consumer = KafkaConsumer(
                settings.kafka_topic,
                bootstrap_servers=settings.kafka_brokers_list,
                group_id=settings.kafka_group_id,
                auto_offset_reset=settings.kafka_auto_offset_reset,
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                session_timeout_ms=6000,
                request_timeout_ms=30000,
            )
            logger.info(f"Connected to Kafka topic: {settings.kafka_topic}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise

    def process_event(self, event: Dict[str, Any]) -> bool:
        """
        Process a single event from Kafka.

        Args:
            event: Event dictionary with user_id, destination_id, event_type, etc.

        Returns:
            True if event was processed successfully
        """
        try:
            user_id = event.get("user_id")
            destination_id = event.get("destination_id")
            event_type = event.get("event_type")
            rating = event.get("rating")

            if not all([user_id, destination_id, event_type]):
                logger.warning(f"Incomplete event data: {event}")
                return False

            session = get_session()
            try:
                recommender = RecommenderService(session)
                success = recommender.process_event(
                    user_id=user_id,
                    destination_id=destination_id,
                    event_type=event_type,
                    rating=rating,
                )

                if success:
                    logger.info(
                        f"Processed event: user={user_id}, dest={destination_id}, type={event_type}"
                    )
                else:
                    logger.error(f"Failed to process event: {event}")

                return success
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error processing event {event}: {e}")
            return False

    def run(self) -> None:
        """Run the consumer loop."""
        self.running = True
        logger.info("Event consumer started")

        try:
            for message in self.consumer:
                try:
                    event = message.value
                    logger.debug(f"Received event: {event}")
                    self.process_event(event)

                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the consumer."""
        self.running = False
        if self.consumer:
            self.consumer.close()
        logger.info("Event consumer stopped")


def run_consumer():
    """Start the Kafka event consumer."""
    # Initialize database
    logger.info(f"Initializing database: {settings.database_url}")
    init_db()

    # Populate default data
    session = get_session()
    try:
        recommender = RecommenderService(session)
        recommender.ensure_default_destinations()
    finally:
        session.close()

    # Start consumer
    consumer = EventConsumer()
    try:
        consumer.connect()
        consumer.run()
    except Exception as e:
        logger.error(f"Fatal error in consumer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_consumer()
