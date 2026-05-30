"""Stores current execution run state."""

from __future__ import annotations


class ExecutionMemory:
    def __init__(self):
        self._results: list[dict] = []
        self._current_session: str = ""

    def set_session(self, session_id: str) -> None:
        self._current_session = session_id
        self._results = []

    def add_result(self, result: dict) -> None:
        self._results.append(result)

    def get_results(self) -> list[dict]:
        return list(self._results)

    def get_session(self) -> str:
        return self._current_session


execution_memory = ExecutionMemory()
