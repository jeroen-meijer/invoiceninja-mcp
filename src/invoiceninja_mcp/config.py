"""Configuration management for InvoiceNinja MCP Server."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """InvoiceNinja API settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Required settings
    api_url: str
    api_key: str

    # Optional settings with defaults
    invoiceninja_timeout: int = 30
    invoiceninja_max_retries: int = 3


# Global settings instance
settings = Settings()
