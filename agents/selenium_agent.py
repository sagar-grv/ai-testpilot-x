"""SeleniumAgent — generates Python Selenium code per test case."""

from __future__ import annotations
from agents.base_agent import BaseAgent
from schemas.testcase_schema import TestCaseSchema
from monitoring.logger import get_logger

log = get_logger(__name__)


class SeleniumAgent(BaseAgent):
    agent_name = "SeleniumAgent"

    def __init__(self):
        super().__init__()
        self.scripts: dict[str, str] = {}

    def generate_for_tc(self, tc: TestCaseSchema, target_url: str = "") -> str:
        """Generate a Selenium test function string for one test case."""
        self.log.info(f"SeleniumAgent.generate_for_tc | tc_id={tc.id}")
        prompt_template = self._load_prompt("selenium_prompt.txt")
        prompt = prompt_template.format(
            tc_id=tc.id,
            title=tc.title,
            steps="\n".join(f"- {s}" for s in tc.steps),
            expected_result=tc.expected_result,
            target_url=target_url or "https://example.com",
        )
        code = self._call_llm(prompt).strip()
        # Strip markdown fences if present
        if code.startswith("```"):
            lines = code.split("\n")
            code = "\n".join(lines[1:-1]) if len(lines) > 2 else code
            code = code.strip("`").strip()
        self.scripts[tc.id] = code
        return code

    def generate_all(
        self, test_cases: list[TestCaseSchema], target_url: str = ""
    ) -> dict[str, str]:
        """Generate scripts for all test cases. Returns {tc_id: code}."""
        for tc in test_cases:
            self.generate_for_tc(tc, target_url)
        return dict(self.scripts)
