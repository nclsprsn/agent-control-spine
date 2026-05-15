from pydantic_settings import BaseSettings


class SpineSettings(BaseSettings):
    database_url: str = "postgresql+asyncpg://spine:spine-dev-password@localhost:5432/spine"
    redis_url: str = "redis://localhost:6379/0"
    nats_url: str = "nats://localhost:4222"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "spine"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8080

    model_config = {"env_prefix": "", "case_sensitive": False}
