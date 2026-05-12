"""Application configuration loaded from .env file."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    minimax_api_key: str
    minimax_base_url: str = "https://api.minimaxi.com/v1"
    minimax_model: str = "MiniMax-M2.7"
    tavily_api_key: str
    sqlite_path: str = "./backend/data/sqlite.db"
    chroma_path: str = "./backend/chroma_db/"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"

    model_config = {
        "env_file": str(Path(__file__).parent.parent.parent.parent / ".env"),
        "env_file_encoding": "utf-8",
    }


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
