"""Configuration management for the agentic AI system."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # LLM Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-opus-20240229"

    # Logging
    log_level: str = "INFO"
    json_logging: bool = True

    # System
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
