"""TestCaseAgent — generates test cases from RequirementSchema using RAG context."""
from __future__ import annotations
from agents.base_agent import BaseAgent
from schemas.requirement_schema import RequirementSchema
from schemas.testcase_schema import TestCaseSchema
from core.event_bus import bus, EventType
from core.rag_engine import rag_engine
from config import settings
from monitoring.logger import get_logger

log = get_logger(__name__)
_VALID_TYPES = {"Positive", "Negative", "Security", "Performance", "Boundary", "Accessibility"}
_VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}


class TestCaseAgent(BaseAgent):
    agent_name = "TestCaseAgent"

    def run(self, requirement: RequirementSchema) -> list[TestCaseSchema]:
        self.log.info(f"TestCaseAgent.run | modules={requirement.modules}")
        # RAG: get similar past test cases for context
        rag_context = ""
        try:
            query = f"{' '.join(requirement.modules)} test cases"
            matches = rag_engine.query("testcases", query, n=settings.RAG_TOP_K)
            if matches:
                rag_context = "\n".join(f"- {m['text'][:100]}" for m in matches)
        except Exception as e:
            self.log.warning(f"RAG query failed, continuing without context: {e}")

        prompt_template = self._load_prompt("testcase_prompt.txt")
        all_test_cases = []
        idx = 1
        for module in requirement.modules:
            prompt = prompt_template.format(
                module_name=module,
                requirement_context=requirement.raw_input,
                rag_context=rag_context or "No past test cases available.",
            )
            raw = self._call_llm(prompt)
            items = self._parse_json(raw)
            if not isinstance(items, list):
                items = [items]
            for item in items:
                tc = TestCaseSchema(
                    id=f"TC{idx:02d}",
                    title=item.get("title", f"Test {idx}"),
                    module=module,
                    type=item.get("type", "Positive") if item.get("type") in _VALID_TYPES else "Positive",
                    priority=item.get("priority", "Medium") if item.get("priority") in _VALID_PRIORITIES else "Medium",
                    steps=item.get("steps", []),
                    expected_result=item.get("expected_result", ""),
                    confidence_score=float(item.get("confidence_score", 0.7)),
                )
                all_test_cases.append(tc)
                idx += 1

        bus.emit(EventType.TESTCASES_GENERATED, {"count": len(all_test_cases)})
        self.log.info(f"TestCaseAgent complete | count={len(all_test_cases)}")
        return all_test_cases
