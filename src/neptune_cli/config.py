from pydantic_settings import BaseSettings, SettingsConfigDict

from platformdirs import user_config_dir

from pathlib import Path,PosixPath
import json
import os


class CLISettings(BaseSettings):
    """Configuration settings for the Neptune CLI."""

    # Local development: use `NEPTUNE_API_BASE_URL=http://localhost:8000/v1`
    api_base_url: str = os.environ.get("NETPUNE_API_BASE_URL", "https://neptune.shuttle.dev/v1")
    
    access_token: str | None = None

    class Config:
        model_config = SettingsConfigDict(
            env_prefix="NEPTUNE_",
            json_file=Path(user_config_dir("neptune")) / "config.json",
        )

    json_file: PosixPath | None = Config.model_config.get("json_file")
    def _read_access_token(json_file: str):
        with open(json_file, "r") as f:
            data = json.load(f)
            return data.get("access_token")

    if json_file and json_file.exists():
        access_token = _read_access_token(json_file)

    def save_to_file(self) -> None:
        """Save the current settings to the configuration file."""
        config_path = Path(user_config_dir("neptune"))
        config_path.mkdir(parents=True, exist_ok=True)
        with open(config_path / "config.json", "w") as f:
            f.write(self.model_dump_json())


SETTINGS = CLISettings()
