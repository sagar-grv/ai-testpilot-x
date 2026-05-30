"""ReportAgent — generates GO/GO_WITH_RISK/NO_GO release decision + executive summary."""
from __future__ import annotations
from datetime import datetime, timezone
from agents.base_agent import BaseAgent
from schemas.report_schema import ReportSchema
from schemas.bug_schema import BugSchema, BugClusterSchema
from schemas.execution_schema import ExecutionSchema
from core.event_bus import bus, EventType
from monitoring.logger import get_logger

log = get_logger(__name__)


class ReportAgent(BaseAgent):
    agent_name = "ReportAgent"

    def _determine_decision(self, bugs: list[BugSchema]) -> str:
        """Deterministic decision logic — NO LLM needed."""
        if any(b.severity == "Critical" for b in bugs):
            return "NO_GO"
        if any(b.severity == "High" for b in bugs):
            return "GO_WITH_RISK"
        return "GO"

    def run(
        self,
        execution: ExecutionSchema | None,
        bugs: list[BugSchema],
        clusters: list[BugClusterSchema],
        session_id: str,
    ) -> ReportSchema:
        self.log.info(f"ReportAgent.run | session={session_id} | bugs={len(bugs)}")

        # Compute counts
        total = execution.total if execution else 0
        passed = execution.passed if execution else 0
        failed = execution.failed if execution else 0
        critical = sum(1 for b in bugs if b.severity == "Critical")
        high = sum(1 for b in bugs if b.severity == "High")
        medium = sum(1 for b in bugs if b.severity == "Medium")
        low = sum(1 for b in bugs if b.severity == "Low")

        decision = self._determine_decision(bugs)

        # LLM generates narrative + risk score only
        cluster_summary = "; ".join(f"{c.root_cause_summary} ({c.count} bugs)" for c in clusters)
        try:
            prompt_template = self._load_prompt("report_prompt.txt")
            prompt = prompt_template.format(
                total_tests=total, passed=passed, failed=failed,
                critical_bugs=critical, high_bugs=high, medium_bugs=medium, low_bugs=low,
                cluster_summary=cluster_summary or "No bug clusters",
                decision=decision,
            )
            raw = self._call_llm(prompt)
            data = self._parse_json(raw)
            recommendation = str(data.get("recommendation_text", self._default_recommendation(decision)))
            risk_score = float(data.get("risk_score", self._default_risk_score(decision)))
            confidence = float(data.get("confidence_score", 0.8))
        except Exception as e:
            self.log.warning(f"ReportAgent LLM failed, using defaults: {e}")
            recommendation = self._default_recommendation(decision)
            risk_score = self._default_risk_score(decision)
            confidence = 0.7

        report = ReportSchema(
            session_id=session_id,
            total_tests=total,
            passed=passed,
            failed=failed,
            critical_bugs=critical,
            high_bugs=high,
            medium_bugs=medium,
            low_bugs=low,
            decision=decision,
            recommendation_text=recommendation,
            risk_score=risk_score,
            created_at=datetime.now(timezone.utc).isoformat(),
            confidence_score=confidence,
        )

        # Persist
        try:
            from storage.db import get_session
            from storage.models.reports import ReportRecord
            import json
            db = get_session()
            db.add(ReportRecord(
                session_id=session_id,
                decision=decision,
                summary=recommendation,
                report_json=json.dumps(report.model_dump()),
                created_at=datetime.now(timezone.utc),
            ))
            db.commit()
            db.close()
        except Exception as e:
            self.log.warning(f"ReportAgent SQLite persist failed: {e}")

        # Index in RAG
        try:
            from core.rag_engine import rag_engine
            rag_engine.upsert("reports", f"report-{session_id}",
                              f"{decision} {recommendation}", {"session_id": session_id, "decision": decision})
        except Exception as e:
            self.log.warning(f"ReportAgent RAG upsert failed: {e}")

        bus.emit(EventType.REPORT_GENERATED, {"decision": decision, "session_id": session_id})
        self.log.info(f"ReportAgent complete | decision={decision}")
        return report

    def _default_recommendation(self, decision: str) -> str:
        defaults = {
            "NO_GO": "Release is blocked due to critical defects that must be resolved before deployment.",
            "GO_WITH_RISK": "Release can proceed with caution. High-severity bugs have been identified and should be tracked.",
            "GO": "All tests passed with acceptable quality. Release is approved.",
        }
        return defaults.get(decision, "Release decision requires manual review.")

    def _default_risk_score(self, decision: str) -> float:
        return {"NO_GO": 85.0, "GO_WITH_RISK": 45.0, "GO": 10.0}.get(decision, 50.0)
