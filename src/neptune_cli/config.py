from pydantic_settings import BaseSettings, SettingsConfigDict


class CLISettings(BaseSettings):
    """Configuration settings for the Shuttle Impulse CLI."""

    api_base_url: str = "http://localhost:8000/v1"

    class Config:
        model_config = SettingsConfigDict(env_prefix="SHUTTLE_")


SETTINGS = CLISettings()
