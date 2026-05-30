"""BugAgent — analyzes test failures, correlates with RAG, clusters by root cause."""
from __future__ import annotations
import re
from datetime import datetime, timezone
from agents.base_agent import BaseAgent
from schemas.bug_schema import BugSchema, BugClusterSchema
from schemas.execution_schema import ExecutionSchema
from core.event_bus import bus, EventType
from memory.bug_memory import BugMemory
from config import settings
from monitoring.logger import get_logger

log = get_logger(__name__)

_SEVERITY_ORDER = ["Critical", "High", "Medium", "Low"]


def _extract_failure_signature(error_message: str) -> str:
    """Extract a short signature from an error message."""
    first_line = error_message.split("\n")[0]
    # Remove special chars except underscore
    sig = re.sub(r"[^a-zA-Z0-9_\s]", "", first_line)
    sig = re.sub(r"\s+", "_", sig.strip())
    return sig[:50]


class BugAgent(BaseAgent):
    agent_name = "BugAgent"

    def __init__(self):
        super().__init__()
        self.memory = BugMemory()

    def analyze_single(self, error_message: str, session_id: str, index: int = 0) -> BugSchema:
        """Analyze one failure. Returns BugSchema."""
        self.log.info(f"BugAgent.analyze_single | session={session_id} | index={index}")
        signature = _extract_failure_signature(error_message)

        # RAG: get similar past bugs
        rag_matches = self.memory.get_similar_bugs(signature, n=settings.RAG_TOP_K)
        rag_context = "\n".join(f"- {m.get('text', '')[:100]}" for m in rag_matches)
        if not rag_context:
            rag_context = "No similar past bugs found."

        prompt_template = self._load_prompt("bug_prompt.txt")
        prompt = prompt_template.format(
            failure_details=error_message,
            rag_context=rag_context,
        )

        try:
            raw = self._call_llm(prompt)
            data = self._parse_json(raw)
        except Exception as e:
            self.log.warning(f"BugAgent LLM/parse failed, using defaults: {e}")
            data = {
                "title": f"Test failure: {signature[:40]}",
                "severity": "Medium",
                "priority": "P3",
                "failure_signature": signature,
                "root_cause": error_message[:100],
                "root_cause_confidence": 0.5,
                "fix_suggestion": "Manual investigation required",
                "fix_confidence": 0.3,
                "severity_confidence": 0.5,
            }

        bug_id = f"BUG-{session_id}-{index:03d}"
        bug = BugSchema(
            id=bug_id,
            title=str(data.get("title", f"Failure {index}")),
            severity=data.get("severity", "Medium") if data.get("severity") in ["Critical", "High", "Medium", "Low"] else "Medium",
            priority=data.get("priority", "P3") if data.get("priority") in ["P1", "P2", "P3", "P4"] else "P3",
            failure_signature=str(data.get("failure_signature", signature)),
            root_cause=str(data.get("root_cause", "")),
            root_cause_confidence=float(data.get("root_cause_confidence", 0.5)),
            fix_suggestion=str(data.get("fix_suggestion", "")),
            fix_confidence=float(data.get("fix_confidence", 0.5)),
            severity_confidence=float(data.get("severity_confidence", 0.5)),
            rag_matches=rag_matches,
        )

        # Store in RAG for future correlation
        self.memory.store_bug(session_id, bug.id, bug.title, bug.root_cause,
                              bug.failure_signature, bug.severity)

        # Persist to SQLite
        try:
            from storage.db import get_session
            from storage.models.bugs import BugRecord
            db = get_session()
            db.add(BugRecord(
                session_id=session_id,
                bug_id=bug.id,
                title=bug.title,
                severity=bug.severity,
                priority=bug.priority,
                failure_signature=bug.failure_signature,
                root_cause=bug.root_cause,
                root_cause_confidence=bug.root_cause_confidence,
                fix_suggestion=bug.fix_suggestion,
                fix_confidence=bug.fix_confidence,
                severity_confidence=bug.severity_confidence,
                created_at=datetime.now(timezone.utc),
            ))
            db.commit()
            db.close()
        except Exception as e:
            self.log.warning(f"BugAgent SQLite persist failed: {e}")

        return bug

    def _cluster_bugs(self, bugs: list[BugSchema]) -> list[BugClusterSchema]:
        """Group bugs by first keyword of root_cause."""
        clusters: dict[str, list[BugSchema]] = {}
        for bug in bugs:
            key = bug.root_cause.split()[0].lower() if bug.root_cause.split() else "unknown"
            clusters.setdefault(key, []).append(bug)

        result = []
        for idx, (key, group) in enumerate(clusters.items()):
            severities = [b.severity for b in group]
            top_severity = next((s for s in _SEVERITY_ORDER if s in severities), "Low")
            result.append(BugClusterSchema(
                cluster_id=f"CLUSTER-{idx:03d}",
                root_cause_summary=f"{key.capitalize()} related failure",
                bug_ids=[b.id for b in group],
                severity=top_severity,
                count=len(group),
            ))
        return result

    def run(self, execution: ExecutionSchema, session_id: str) -> tuple[list[BugSchema], list[BugClusterSchema]]:
        """Analyze all failed tests. Returns (bugs, clusters)."""
        failed = [r for r in execution.results if r.status in ("FAIL", "ERROR")]
        self.log.info(f"BugAgent.run | failed_count={len(failed)}")
        bugs = []
        for idx, result in enumerate(failed):
            bug = self.analyze_single(result.error_message or result.status, session_id, index=idx)
            bugs.append(bug)
        clusters = self._cluster_bugs(bugs)
        bus.emit(EventType.BUG_ANALYZED, {"count": len(bugs), "clusters": len(clusters)})
        return bugs, clusters
