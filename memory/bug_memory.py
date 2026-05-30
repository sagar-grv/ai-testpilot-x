"""Bug memory — RAG-backed storage for past bugs."""

from __future__ import annotations
from monitoring.logger import get_logger

log = get_logger(__name__)


class BugMemory:
    def get_similar_bugs(self, signature: str, n: int = 5) -> list[dict]:
        try:
            from core.rag_engine import rag_engine

            return rag_engine.query("bugs", signature, n=n)
        except Exception as e:
            log.warning(f"BugMemory.get_similar_bugs failed: {e}")
            return []

    def store_bug(
        self,
        session_id: str,
        bug_id: str,
        title: str,
        root_cause: str,
        failure_signature: str,
        severity: str,
    ) -> None:
        try:
            from core.rag_engine import rag_engine

            text = f"{title} {root_cause} {failure_signature}"
            rag_engine.upsert(
                "bugs", bug_id, text, {"severity": severity, "session_id": session_id}
            )
        except Exception as e:
            log.warning(f"BugMemory.store_bug failed: {e}")


bug_memory = BugMemory()
