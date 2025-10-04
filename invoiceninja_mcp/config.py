from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    api_url: str
    api_key: str
    invoiceninja_timeout: int = 30
    invoiceninja_max_retries: int = 3


settings = Settings()
