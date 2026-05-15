from spine_common.config import SpineSettings


class RegistrySettings(SpineSettings):
    otel_service_name: str = "registry"
    host: str = "0.0.0.0"
    port: int = 8081
