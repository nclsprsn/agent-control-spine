from spine_common.config import SpineSettings


class ObserverSettings(SpineSettings):
    otel_service_name: str = "observer"
    host: str = "0.0.0.0"
    port: int = 8083
