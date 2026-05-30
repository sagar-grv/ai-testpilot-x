"""config.py — Single source of truth for all settings (Pydantic-settings v2).

Supports three sources in priority order:
  1. Streamlit secrets (st.secrets) — when running on Streamlit Cloud
  2. Environment variables / .env file — local development
  3. Hard-coded defaults — fallbacks
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env for local dev (no-op if file doesn't exist)
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)

# ── Pull Streamlit secrets into env vars (cloud deployment) ───────────────────
try:
    import streamlit as st
    if hasattr(st, "secrets") and len(st.secrets) > 0:
        _secret_keys = [
            "GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
            "LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_TRACING",
            "DB_URL", "CHROMA_PATH", "EXECUTION_MODE", "SELENIUM_GRID_URL",
            "APP_ENV", "LOG_LEVEL", "MAX_AGENT_RETRIES",
        ]
        for _key in _secret_keys:
            if _key in st.secrets and _key not in os.environ:
                os.environ[_key] = str(st.secrets[_key])
except Exception:
    pass  # Not running in Streamlit context — skip


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
    LOG_LEVEL: str = Field(default="INFO")
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
