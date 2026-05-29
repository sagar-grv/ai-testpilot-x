"""APIAgent — generates API test suites, optionally executes them."""
from __future__ import annotations
import json
from agents.base_agent import BaseAgent
from schemas.api_test_schema import APITestResultSchema
from schemas.requirement_schema import RequirementSchema
from monitoring.logger import get_logger

log = get_logger(__name__)

_VALID_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH"}


class APIAgent(BaseAgent):
    agent_name = "APIAgent"

    def run_for_module(self, module_name: str, requirement: RequirementSchema | None) -> list[APITestResultSchema]:
        """Generate API tests for one module."""
        self.log.info(f"APIAgent.run_for_module | module={module_name}")
        req_context = requirement.raw_input if requirement else "No additional context."
        prompt_template = self._load_prompt("api_prompt.txt")
        prompt = prompt_template.format(
            module_name=module_name,
            requirement_context=req_context,
        )
        raw = self._call_llm(prompt)
        items = self._parse_json(raw)
        if not isinstance(items, list):
            items = [items]
        results = []
        for item in items:
            try:
                method = str(item.get("method", "GET")).upper()
                if method not in _VALID_METHODS:
                    method = "GET"
                results.append(APITestResultSchema(
                    method=method,
                    endpoint=str(item.get("endpoint", "/")),
                    body=item.get("body") or {},
                    expected_status=int(item.get("expected_status", 200)),
                    assertion=str(item.get("assertion", "")),
                ))
            except Exception as e:
                self.log.warning(f"APIAgent skipping malformed item: {e}")
        self.log.info(f"APIAgent complete | module={module_name} | count={len(results)}")
        return results

    def run(self, requirement: RequirementSchema) -> dict[str, list[APITestResultSchema]]:
        """Generate API tests for all modules."""
        modules = requirement.modules if requirement.modules else ["Default"]
        suite: dict[str, list[APITestResultSchema]] = {}
        for module in modules:
            suite[module] = self.run_for_module(module, requirement)
        return suite
