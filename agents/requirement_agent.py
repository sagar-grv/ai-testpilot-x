"""RequirementAgent — parses user story into structured RequirementSchema."""

from __future__ import annotations
from agents.base_agent import BaseAgent
from schemas.requirement_schema import RequirementSchema
from core.event_bus import bus, EventType
from monitoring.logger import get_logger

log = get_logger(__name__)


class RequirementAgent(BaseAgent):
    agent_name = "RequirementAgent"

    def run(self, user_story: str) -> RequirementSchema:
        self.log.info(f"RequirementAgent.run | story_len={len(user_story)}")
        prompt_template = self._load_prompt("requirement_prompt.txt")
        prompt = prompt_template.format(user_story=user_story)
        raw = self._call_llm(prompt)
        data = self._parse_json(raw)
        schema = RequirementSchema(
            modules=data.get("modules", []),
            risk_areas=data.get("risk_areas", []),
            priority=data.get("priority", "Medium"),
            confidence_score=float(data.get("confidence_score", 0.7)),
            raw_input=user_story,
        )
        bus.emit(
            EventType.REQUIREMENT_ANALYZED,
            {"modules": schema.modules, "priority": schema.priority},
        )
        self.log.info(f"RequirementAgent complete | modules={schema.modules}")
        return schema
