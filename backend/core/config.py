"""
Application configuration for the AI Prompt Agent.

This module provides a single, validated configuration object
for the entire application.

Configuration values are loaded from environment variables
and the local .env file through Pydantic Settings.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.

    Values are loaded from environment variables and, during
    local development, from the project's .env file.
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
        description="Default Ollama model.",
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
    # Ollama Request Configuration
    # --------------------------------------------------------
    # --------------------------------------------------------
    # Groq Configuration
    # --------------------------------------------------------

    groq_api_key: str = Field(
        default="",
        description="Groq API key.",
    )

    groq_model: str = Field(
        default="llama-3.1-8b-instant",
        description="Default Groq model.",
    )

    # --------------------------------------------------------
    # Ollama Request Configuration
    # --------------------------------------------------------

    ollama_timeout_seconds: int = Field(
        default=120,
        gt=0,
        description="Maximum time allowed for an Ollama request.",
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
    Return the application's cached Settings instance.

    Caching ensures that the application does not repeatedly
    reload and parse the environment configuration.
    """

    return Settings()


settings = get_settings()