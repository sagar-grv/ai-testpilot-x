"""VerificationAgent — checks test case coverage, duplicates, missing edge cases."""
from __future__ import annotations
from agents.base_agent import BaseAgent
from schemas.testcase_schema import TestCaseSchema
from schemas.verification_schema import VerificationSchema
from core.event_bus import bus, EventType
from config import settings
from monitoring.logger import get_logger
import json

log = get_logger(__name__)


class VerificationAgent(BaseAgent):
    agent_name = "VerificationAgent"

    def run(self, test_cases: list[TestCaseSchema], retry_count: int = 0) -> VerificationSchema:
        self.log.info(f"VerificationAgent.run | tc_count={len(test_cases)}")
        if not test_cases:
            return VerificationSchema(coverage_score=0.0, duplicate_count=0, missing_edge_cases=["No test cases provided"], passed=False)

        # Try AI-based verification, fall back to heuristic
        try:
            schema = self._ai_verify(test_cases)
        except Exception as e:
            self.log.warning(f"AI verification failed, using heuristic: {e}")
            schema = self._heuristic_verify(test_cases)

        schema = VerificationSchema(
            coverage_score=schema.coverage_score,
            duplicate_count=schema.duplicate_count,
            missing_edge_cases=schema.missing_edge_cases,
            passed=schema.coverage_score >= settings.VERIFICATION_COVERAGE_THRESHOLD,
            retry_count=retry_count,
            confidence_score=schema.confidence_score,
        )

        # Retry loop: if not passed and within retry limit, could be triggered by caller
        bus.emit(EventType.VERIFICATION_COMPLETE, {"passed": schema.passed, "coverage": schema.coverage_score})
        self.log.info(f"VerificationAgent complete | passed={schema.passed} | coverage={schema.coverage_score:.2f}")
        return schema

    def _ai_verify(self, test_cases: list[TestCaseSchema]) -> VerificationSchema:
        prompt_template = self._load_prompt("verification_prompt.txt")
        tcs_json = json.dumps([tc.model_dump() for tc in test_cases], indent=2)
        prompt = prompt_template.format(
            testcases_json=tcs_json,
            requirement_context="General software module",
        )
        raw = self._call_llm(prompt)
        data = self._parse_json(raw)
        return VerificationSchema(
            coverage_score=float(data.get("coverage_score", 0.7)),
            duplicate_count=int(data.get("duplicate_count", 0)),
            missing_edge_cases=data.get("missing_edge_cases", []),
            passed=bool(data.get("passed", True)),
            confidence_score=float(data.get("confidence_score", 0.7)),
        )

    def _heuristic_verify(self, test_cases: list[TestCaseSchema]) -> VerificationSchema:
        """Simple heuristic: check type coverage."""
        types_present = {tc.type for tc in test_cases}
        all_types = {"Positive", "Negative", "Security", "Boundary"}
        coverage = len(types_present & all_types) / len(all_types)
        titles = [tc.title.lower() for tc in test_cases]
        duplicates = len(titles) - len(set(titles))
        missing = []
        if "Security" not in types_present:
            missing.append("Security test cases (SQL injection, XSS)")
        if "Boundary" not in types_present:
            missing.append("Boundary value test cases")
        return VerificationSchema(
            coverage_score=coverage,
            duplicate_count=duplicates,
            missing_edge_cases=missing,
            passed=coverage >= settings.VERIFICATION_COVERAGE_THRESHOLD,
            confidence_score=0.6,
        )
