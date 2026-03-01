"""Configuration management for the recommender service."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Database
    database_url: str = "sqlite:///./recommender.db"
    db_echo: bool = False

    # Kafka
    kafka_brokers: str = "localhost:29092"
    kafka_topic: str = "user-events"
    kafka_group_id: str = "recommender-consumer"
    kafka_auto_offset_reset: str = "earliest"

    # gRPC Server
    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50051

    # Service
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def kafka_brokers_list(self) -> list[str]:
        """Parse comma-separated kafka brokers into list."""
        return [broker.strip() for broker in self.kafka_brokers.split(",")]


# Global settings instance
settings = Settings()
