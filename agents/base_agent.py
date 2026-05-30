"""BaseAgent — shared interface for all AI TestPilot X agents."""

from __future__ import annotations
import json
import re
from abc import ABC
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
from core.llm_client import LLMClient
from core.event_bus import bus, EventType
from monitoring.logger import get_logger
from schemas.error_schema import ErrorSchema

log = get_logger(__name__)

# Maximum input length accepted by any agent (chars).
# Prevents token stuffing, prompt injection via oversized payloads, and
# accidental billing explosions from unbounded stdin reads.
MAX_INPUT_LENGTH = 15_000

# Control characters and null bytes that can confuse LLM tokenizers
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _find_prompts_dir() -> Path:
    """Locate prompts/ directory — works both from source and installed package."""
    # Try relative to this file (works when running from source)
    candidates = [
        Path(__file__).parent.parent / "prompts",  # source layout: agents/../prompts
        Path(__file__).parent / "prompts",  # flat layout
        Path.cwd() / "prompts",  # cwd fallback
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return c

    # Try importlib.resources (installed package)
    try:
        import importlib.resources as pkg_resources

        ref = pkg_resources.files("prompts")
        # Convert to a real Path by traversing to a known file
        p = Path(str(ref))
        if p.exists():
            return p
    except Exception:
        pass

    # Return best guess even if it doesn't exist yet
    return Path(__file__).parent.parent / "prompts"


PROMPTS_DIR = _find_prompts_dir()


class BaseAgent(ABC):
    """All agents inherit this. Provides LLM access, prompt loading, and error handling."""

    agent_name: str = "BaseAgent"

    def __init__(self, provider: str = "gemini"):
        self.client = LLMClient(provider=provider)
        self.log = get_logger(self.__class__.__name__)

    # ------------------------------------------------------------------
    # SECURITY: input sanitization — call before embedding user data in prompts
    # ------------------------------------------------------------------
    def _sanitize_input(
        self,
        text: str,
        field: str = "input",
        max_length: int = MAX_INPUT_LENGTH,
    ) -> str:
        """Validate and sanitize user-supplied text before use in LLM prompts.

        Raises:
            ValueError: if input exceeds max_length or is not a string.
        """
        if not isinstance(text, str):
            raise ValueError(f"{field} must be a string, got {type(text).__name__}")
        # Strip null bytes and non-printable control characters
        cleaned = _CONTROL_CHAR_RE.sub("", text)
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
        cleaned = cleaned.strip()
        if len(cleaned) > max_length:
            raise ValueError(
                f"{field} exceeds maximum allowed length "
                f"({len(cleaned)} > {max_length} chars). "
                f"Please shorten your input."
            )
        return cleaned

    def _load_prompt(self, prompt_file: str) -> str:
        path = PROMPTS_DIR / prompt_file
        if not path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {path}\n"
                f"PROMPTS_DIR resolved to: {PROMPTS_DIR}"
            )
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
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        bus.emit(EventType.AGENT_FAILED, {"error": err.model_dump()})
        self.log.error(f"Agent failed: {error}")
        if state is not None:
            if "agent_errors" not in state or state["agent_errors"] is None:
                state["agent_errors"] = []
            state["agent_errors"].append(err.model_dump())
