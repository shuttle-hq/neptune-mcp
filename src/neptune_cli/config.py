from pydantic_settings import BaseSettings, SettingsConfigDict

from platformdirs import user_config_dir

from pathlib import Path


class CLISettings(BaseSettings):
    """Configuration settings for the Neptune CLI."""

    api_base_url: str = "http://localhost:8000/v1"
    
    access_token: str | None = None

    class Config:
        model_config = SettingsConfigDict(
            env_prefix="NEPTUNE_",
            json_file=Path(user_config_dir("neptune")) / "config.json",
        )

    def save_to_file(self) -> None:
        """Save the current settings to the configuration file."""
        config_path = Path(user_config_dir("neptune"))
        config_path.mkdir(parents=True, exist_ok=True)
        with open(config_path / "config.json", "w") as f:
            f.write(self.model_dump_json())


SETTINGS = CLISettings()
