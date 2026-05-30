"""config.py — Unified settings for both CLI and Streamlit modes.

Priority order:
  1. Programmatic override via configure(**kwargs)
  2. testpilot.yaml in current working directory
  3. Environment variables / .env file
  4. Hard-coded defaults
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Literal, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env for local dev (no-op if file doesn't exist)
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)


def load_yaml_config(path: str | Path | None = None) -> dict:
    """Load a testpilot.yaml / testpilot.toml config file into os.environ.

    Called explicitly by CLI commands and app.py — never at import time.
    """
    import yaml

    candidates = [path] if path else [
        Path.cwd() / "testpilot.yaml",
        Path.cwd() / "testpilot.yml",
        Path.cwd() / "testpilot.toml",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            with open(candidate, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            # Expand ${ENV_VAR} references
            for k, v in data.items():
                if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                    env_key = v[2:-1]
                    data[k] = os.environ.get(env_key, "")
            # Push into env (only if not already set — don't override real env vars)
            for k, v in data.items():
                key_upper = k.upper()
                if key_upper not in os.environ and v is not None:
                    os.environ[key_upper] = str(v)
            return data
    return {}


def load_streamlit_secrets() -> None:
    """Pull Streamlit Cloud secrets into os.environ.

    Must be called EXPLICITLY from app.py startup — never at import time.
    This avoids importing streamlit in headless/CLI contexts.
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets") and len(st.secrets) > 0:
            _keys = [
                "GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                "LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_TRACING",
                "DB_URL", "CHROMA_PATH", "EXECUTION_MODE", "SELENIUM_GRID_URL",
                "APP_ENV", "LOG_LEVEL", "MAX_AGENT_RETRIES",
            ]
            for k in _keys:
                if k in st.secrets and k not in os.environ:
                    os.environ[k] = str(st.secrets[k])
    except Exception:
        pass


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
    LOG_LEVEL: str = Field(default="WARNING")
    MAX_AGENT_RETRIES: int = Field(default=2)
    RAG_TOP_K: int = Field(default=5)
    VERIFICATION_COVERAGE_THRESHOLD: float = Field(default=0.6)
    VERIFICATION_LOW_CONFIDENCE_MAX: float = Field(default=0.30)

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
        # Prefer .testpilot/ in cwd when running as CLI tool
        cwd_artifacts = Path.cwd() / ".testpilot" / "artifacts"
        if cwd_artifacts.parent.exists():
            return cwd_artifacts
        return self.BASE_DIR / "execution" / "artifacts"


# Global singleton — re-instantiate after calling load_yaml_config() / configure()
settings = Settings()


def configure(**kwargs: Any) -> None:
    """Programmatically override settings. Call before any agent is used.

    Example::

        from config import configure
        configure(gemini_api_key="AIzaSy...", execution_mode="MOCK")
    """
    global settings
    for k, v in kwargs.items():
        os.environ[k.upper()] = str(v)
    settings = Settings()


def reload_settings() -> None:
    """Force re-read of all env vars into the global settings singleton."""
    global settings
    settings = Settings()
