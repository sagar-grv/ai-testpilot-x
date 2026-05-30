"""Cross-agent context passing — stores requirement and test context for current session."""

from __future__ import annotations
from typing import Any


class ConversationMemory:
    def __init__(self):
        self._context: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._context[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._context.get(key, default)

    def clear(self) -> None:
        self._context.clear()

    def as_dict(self) -> dict:
        return dict(self._context)


conversation_memory = ConversationMemory()
