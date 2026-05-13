"""Application configuration loaded from .env file."""

from pathlib import Path
from pydantic_settings import BaseSettings

# Base directory for resolving relative paths — always backend/
_BACKEND_DIR = Path(__file__).parent.parent.parent.resolve()


class Settings(BaseSettings):
    minimax_api_key: str
    minimax_base_url: str = "https://api.minimaxi.com/v1"
    minimax_model: str = "MiniMax-M2.7"
    tavily_api_key: str
    sqlite_path: str = str(_BACKEND_DIR / "data" / "sqlite.db")
    chroma_path: str = str(_BACKEND_DIR / "chroma_db")
    embedding_model: str = "BAAI/bge-small-zh-v1.5"

    model_config = {
        "env_file": str(_BACKEND_DIR.parent / ".env"),
        "env_file_encoding": "utf-8",
    }


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
