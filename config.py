"""config.py — Single source of truth for all settings (Pydantic-settings v2)."""
from __future__ import annotations
from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # LLM
    GEMINI_API_KEY: str = Field(default="")
    OPENAI_API_KEY: str = Field(default="")
    ANTHROPIC_API_KEY: str = Field(default="")

    # LangSmith
    LANGSMITH_API_KEY: str = Field(default="")
    LANGSMITH_PROJECT: str = Field(default="ai-testpilot-x")
    LANGSMITH_TRACING: bool = Field(default=False)

    # Database
    DB_URL: str = Field(default="sqlite:///./testpilot.db")

    # ChromaDB
    CHROMA_PATH: str = Field(default="./chroma_db")
    CHROMA_COLLECTION_TESTCASES: str = Field(default="testcases")
    CHROMA_COLLECTION_BUGS: str = Field(default="bugs")
    CHROMA_COLLECTION_REQUIREMENTS: str = Field(default="requirements")
    CHROMA_COLLECTION_REPORTS: str = Field(default="reports")

    # Execution
    EXECUTION_MODE: Literal["LOCAL", "MOCK", "GRID"] = Field(default="MOCK")
    SELENIUM_GRID_URL: str = Field(default="http://localhost:4444/wd/hub")
    SELENIUM_HEADLESS: bool = Field(default=True)

    # App
    APP_ENV: Literal["development", "production"] = Field(default="development")
    LOG_LEVEL: str = Field(default="DEBUG")
    MAX_AGENT_RETRIES: int = Field(default=2)
    RAG_TOP_K: int = Field(default=5)
    VERIFICATION_COVERAGE_THRESHOLD: float = Field(default=0.6)
    VERIFICATION_LOW_CONFIDENCE_MAX: float = Field(default=0.30)

    # Paths (computed, not from env)
    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).parent

    @property
    def PROMPTS_DIR(self) -> Path:
        return self.BASE_DIR / "prompts"

    @property
    def KNOWLEDGE_DIR(self) -> Path:
        return self.BASE_DIR / "knowledge"

    @property
    def ARTIFACTS_DIR(self) -> Path:
        return self.BASE_DIR / "execution" / "artifacts"


settings = Settings()
