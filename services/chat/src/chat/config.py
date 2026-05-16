from spine_common.config import SpineSettings


class ChatSettings(SpineSettings):
    otel_service_name: str = "chat"
    host: str = "0.0.0.0"
    port: int = 8084
    registry_url: str = "http://registry:8081"
    catalog_url: str = "http://catalog:8082"
    ollama_base_url: str = "http://ollama:11434/v1"
    llm_model: str = "qwen3:1.7b"
    cors_origins: list[str] = ["http://localhost:3002", "http://localhost:3000"]  # noqa: RUF012
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://langfuse:3000"
    langfuse_enabled: bool = True
