"""
Application configuration for the AI Prompt Agent.

Configuration is loaded from environment variables
and the local .env file through Pydantic Settings.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    """

    # --------------------------------------------------------
    # Application Configuration
    # --------------------------------------------------------

    app_name: str = Field(
        default="AI Prompt Agent",
        description="Application name.",
    )

    app_env: str = Field(
        default="development",
        description="Current application environment.",
    )

    debug: bool = Field(
        default=False,
        description="Enable development debugging.",
    )

    app_version: str = Field(
        default="1.0.0",
        description="Application version.",
    )

    # --------------------------------------------------------
    # Database Configuration
    # --------------------------------------------------------

    database_url: str = Field(
        default="sqlite:///./data/app.db",
        description="SQLAlchemy database connection URL.",
    )

    # --------------------------------------------------------
    # Ollama Configuration
    # --------------------------------------------------------

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL of the local Ollama server.",
    )

    ollama_model: str = Field(
        default="mistral",
        description="Default local Ollama model.",
    )

    ollama_timeout_seconds: int = Field(
        default=120,
        gt=0,
        description="Maximum time allowed for Ollama requests.",
    )

    # --------------------------------------------------------
    # Groq Cloud Configuration
    # --------------------------------------------------------

    groq_api_key: str = Field(
        default="",
        description="Groq Cloud API key.",
    )

    groq_model: str = Field(
        default="openai/gpt-oss-20b",
        description="Default Groq Cloud model.",
    )

    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        description="Groq OpenAI-compatible API base URL.",
    )

    groq_timeout_seconds: int = Field(
        default=60,
        gt=0,
        description="Maximum time allowed for Groq requests.",
    )

    # --------------------------------------------------------
    # Default LLM Parameters
    # --------------------------------------------------------

    default_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default LLM temperature.",
    )

    default_top_p: float = Field(
        default=0.9,
        gt=0.0,
        le=1.0,
        description="Default Top-P value.",
    )

    default_max_tokens: int = Field(
        default=512,
        gt=0,
        description="Default maximum output tokens.",
    )

    # --------------------------------------------------------
    # Pydantic Settings Configuration
    # --------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return the cached application settings.
    """

    return Settings()


settings = get_settings()