"""Synchronous in-process event bus."""

from __future__ import annotations
from collections import defaultdict
from enum import Enum
from typing import Any, Callable
from monitoring.logger import get_logger

log = get_logger(__name__)


class EventType(str, Enum):
    REQUIREMENT_ANALYZED = "REQUIREMENT_ANALYZED"
    TESTCASES_GENERATED = "TESTCASES_GENERATED"
    VERIFICATION_COMPLETE = "VERIFICATION_COMPLETE"
    EXECUTION_APPROVED = "EXECUTION_APPROVED"
    EXECUTION_COMPLETE = "EXECUTION_COMPLETE"
    BUG_ANALYZED = "BUG_ANALYZED"
    HEALING_COMPLETE = "HEALING_COMPLETE"
    REPORT_GENERATED = "REPORT_GENERATED"
    AGENT_FAILED = "AGENT_FAILED"


class EventBus:
    def __init__(self):
        self._listeners: dict[EventType, list[Callable]] = defaultdict(list)
        self._history: list[dict[str, Any]] = []

    def on(self, event_type: EventType):
        def decorator(fn: Callable):
            self._listeners[event_type].append(fn)
            return fn

        return decorator

    def subscribe(self, event_type: EventType, fn: Callable):
        self._listeners[event_type].append(fn)

    def emit(self, event_type: EventType, payload: dict | None = None) -> None:
        payload = payload or {}
        event = {"type": event_type.value, "payload": payload}
        self._history.append(event)
        log.debug(f"EventBus emit | {event_type.value}")
        for listener in self._listeners.get(event_type, []):
            try:
                listener(event)
            except Exception as e:
                log.error(f"EventBus listener error | {event_type} | {e}")

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._history)

    def clear_history(self):
        self._history.clear()


bus = EventBus()
