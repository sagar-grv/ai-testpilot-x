"""BaseAgent — shared interface for all AI TestPilot X agents."""
from __future__ import annotations
import json
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from core.llm_client import LLMClient
from core.event_bus import bus, EventType
from monitoring.logger import get_logger
from monitoring.metrics import timer
from schemas.error_schema import ErrorSchema
from datetime import datetime

log = get_logger(__name__)
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class BaseAgent(ABC):
    """All agents inherit this. Provides LLM access, prompt loading, and error handling."""

    agent_name: str = "BaseAgent"

    def __init__(self, provider: str = "gemini"):
        self.client = LLMClient(provider=provider)
        self.log = get_logger(self.__class__.__name__)

    def _load_prompt(self, prompt_file: str) -> str:
        path = PROMPTS_DIR / prompt_file
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8")

    def _call_llm(self, prompt: str) -> str:
        return self.client.generate(prompt)

    def _parse_json(self, raw: str) -> Any:
        """Strip markdown fences and parse JSON. Raises ValueError on failure."""
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned
        cleaned = cleaned.strip("`").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            self.log.error(f"JSON parse failed: {e}\nRaw: {raw[:200]}")
            raise ValueError(f"Could not parse LLM output as JSON: {e}") from e

    def _emit_failure(self, error: Exception, state: dict | None = None) -> None:
        err = ErrorSchema(
            agent_name=self.agent_name,
            error_type=type(error).__name__,
            message=str(error),
            timestamp=datetime.utcnow().isoformat(),
        )
        bus.emit(EventType.AGENT_FAILED, {"error": err.model_dump()})
        self.log.error(f"Agent failed: {error}")
        if state is not None:
            if "agent_errors" not in state or state["agent_errors"] is None:
                state["agent_errors"] = []
            state["agent_errors"].append(err.model_dump())
