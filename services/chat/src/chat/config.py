from spine_common.config import SpineSettings


class ChatSettings(SpineSettings):
    otel_service_name: str = "chat"
    host: str = "0.0.0.0"
    port: int = 8084
    registry_url: str = "http://registry:8081"
    catalog_url: str = "http://catalog:8082"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://langfuse:3003"
    langfuse_enabled: bool = True
