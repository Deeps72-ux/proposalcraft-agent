import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    GROQ_API_KEY: str = Field(default="", description="Groq API Key")
    GROQ_CHAT_MODEL: str = Field(default="openai/gpt-oss-20b", description="Default Groq LLM model")
    COMPANY_NAME: str = Field(default="ProposalCraft Solutions", description="Company or studio name")
    DEFAULT_CURRENCY: str = Field(default="USD", description="Default currency code")
    HOST: str = Field(default="0.0.0.0", description="API Host")
    PORT: int = Field(default=8000, description="API Port")
    DEBUG: bool = Field(default=False, description="Debug mode")


settings = Settings()
