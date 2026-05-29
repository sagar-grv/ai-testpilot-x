"""config.py — Single source of truth for all settings."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    LANGSMITH_API_KEY: str = Field(default="", env="LANGSMITH_API_KEY")
    LANGSMITH_PROJECT: str = Field(default="ai-testpilot-x", env="LANGSMITH_PROJECT")
    LANGSMITH_TRACING: bool = Field(default=False, env="LANGSMITH_TRACING")
    DB_URL: str = Field(default="sqlite:///./testpilot.db", env="DB_URL")
    CHROMA_PATH: str = Field(default="./chroma_db", env="CHROMA_PATH")
    CHROMA_COLLECTION_TESTCASES: str = Field(default="testcases")
    CHROMA_COLLECTION_BUGS: str = Field(default="bugs")
    CHROMA_COLLECTION_REQUIREMENTS: str = Field(default="requirements")
    CHROMA_COLLECTION_REPORTS: str = Field(default="reports")
    EXECUTION_MODE: Literal["LOCAL", "MOCK", "GRID"] = Field(default="MOCK", env="EXECUTION_MODE")
    SELENIUM_GRID_URL: str = Field(default="http://localhost:4444/wd/hub", env="SELENIUM_GRID_URL")
    SELENIUM_HEADLESS: bool = Field(default=True, env="SELENIUM_HEADLESS")
    APP_ENV: Literal["development", "production"] = Field(default="development", env="APP_ENV")
    LOG_LEVEL: str = Field(default="DEBUG", env="LOG_LEVEL")
    MAX_AGENT_RETRIES: int = Field(default=2, env="MAX_AGENT_RETRIES")
    RAG_TOP_K: int = Field(default=5, env="RAG_TOP_K")
    VERIFICATION_COVERAGE_THRESHOLD: float = Field(default=0.6)
    VERIFICATION_LOW_CONFIDENCE_MAX: float = Field(default=0.30)
    BASE_DIR: Path = Path(__file__).parent
    PROMPTS_DIR: Path = BASE_DIR / "prompts"
    KNOWLEDGE_DIR: Path = BASE_DIR / "knowledge"
    ARTIFACTS_DIR: Path = BASE_DIR / "execution" / "artifacts"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
