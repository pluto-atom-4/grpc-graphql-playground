"""gRPC server entrypoint for the recommender service."""

import logging
import sys
from concurrent import futures

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

import grpc
from generated.pb import recommender_pb2, recommender_pb2_grpc

from app.config.settings import settings
from app.db.session import get_session, init_db
from app.services.recommender import RecommenderService


# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RecommenderServicer(recommender_pb2_grpc.RecommenderServiceServicer):
    """gRPC service implementation for recommendations."""

    def GetRecommendations(self, request, context):
        """Handle GetRecommendations RPC call."""
        try:
            session = get_session()
            try:
                recommender = RecommenderService(session)
                recommendations = recommender.get_recommendations(request.user_id, request.limit)

                destinations = []
                for dest_id, score in recommendations:
                    # Fetch destination details from database
                    from app.db.models import Destination

                    dest = session.query(Destination).filter(Destination.id == dest_id).first()
                    if dest:
                        destinations.append(
                            recommender_pb2.Destination(
                                id=dest.id,
                                name=dest.name,
                                region=dest.region,
                                country=dest.country,
                                description=dest.description or "",
                                latitude=dest.latitude or 0.0,
                                longitude=dest.longitude or 0.0,
                                score=score,
                            )
                        )

                return recommender_pb2.RecommendationResponse(destinations=destinations)
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error in GetRecommendations: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return recommender_pb2.RecommendationResponse()

    def RecordEvent(self, request, context):
        """Handle RecordEvent RPC call."""
        try:
            session = get_session()
            try:
                recommender = RecommenderService(session)
                success = recommender.process_event(
                    request.user_id,
                    request.destination_id,
                    request.event_type,
                    request.rating if request.rating > 0 else None,
                )

                return recommender_pb2.EventResponse(
                    success=success,
                    message="Event recorded successfully" if success else "Failed to record event",
                )
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error in RecordEvent: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return recommender_pb2.EventResponse(success=False, message=str(e))


def serve():
    """Start the gRPC server."""
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

    # Create and start gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    recommender_pb2_grpc.add_RecommenderServiceServicer_to_server(RecommenderServicer(), server)

    address = f"{settings.grpc_host}:{settings.grpc_port}"
    server.add_insecure_port(address)

    logger.info(f"Starting gRPC server on {address}")
    server.start()

    try:
        # Keep server running
        import time

        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server")
        server.stop(0)


if __name__ == "__main__":
    serve()
