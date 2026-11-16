import os
from typing import List
from pydantic import Field
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseConfig
    class BaseSettings:
        pass
    SettingsConfigDict = dict

class Settings(BaseSettings):
    APP_NAME: str = "AquaPulse"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    DEFAULT_REGION: str = "Palghar"
    DEFAULT_STATE: str = "Maharashtra"
    DEFAULT_LATITUDE: float = 19.6967
    DEFAULT_LONGITUDE: float = 72.7655

    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_TIMEOUT_SECONDS: int = 60

    DATABASE_URL: str = "sqlite+aiosqlite:///./aquapulse.db"

    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    SECRET_KEY: str = "aquapulse-dev-secret-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

