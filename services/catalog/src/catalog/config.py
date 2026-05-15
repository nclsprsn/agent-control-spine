from spine_common.config import SpineSettings


class CatalogSettings(SpineSettings):
    otel_service_name: str = "catalog"
    host: str = "0.0.0.0"
    port: int = 8082
