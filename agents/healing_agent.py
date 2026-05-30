"""HealingAgent — recovers broken Selenium selectors using locator hierarchy."""

from __future__ import annotations
import re
from agents.base_agent import BaseAgent
from core.event_bus import bus, EventType
from monitoring.logger import get_logger

log = get_logger(__name__)

LOCATOR_HIERARCHY = [
    "id",
    "name",
    "data-testid",
    "data-cy",
    "css_selector",
    "xpath",
    "semantic_ai",
]


def _extract_selector(error_message: str) -> str:
    """Extract the failed selector from an error message."""
    match = re.search(r"locate element[:\s]+([^\n]+)", error_message, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fall back to first line
    return error_message.split("\n")[0][:100]


class HealingAgent(BaseAgent):
    agent_name = "HealingAgent"

    def attempt_healing(
        self,
        error_message: str,
        target_url: str,
        html_context: str = "",
        tc_id: str = "",
    ) -> dict:
        """Try locator hierarchy to recover a failed selector."""
        original_selector = _extract_selector(error_message)
        self.log.info(f"HealingAgent.attempt_healing | original={original_selector}")
        prompt_template = self._load_prompt("healing_prompt.txt")
        tried_locators = []
        recovered_selector = ""
        success = False
        confidence = 0.0

        for locator_type in LOCATOR_HIERARCHY:
            prompt = prompt_template.format(
                original_selector=original_selector,
                locator_type=locator_type,
                html_context=html_context or "(no HTML context provided)",
            )
            try:
                suggestion = self._call_llm(prompt).strip()
                # Remove any surrounding quotes
                suggestion = suggestion.strip("'\"")
            except Exception as e:
                self.log.warning(
                    f"HealingAgent LLM call failed for {locator_type}: {e}"
                )
                suggestion = ""

            entry = {
                "type": locator_type,
                "suggestion": suggestion,
                "tried": bool(suggestion),
            }
            tried_locators.append(entry)

            if suggestion:
                recovered_selector = suggestion
                success = True
                confidence = 0.8
                self.log.info(
                    f"HealingAgent recovered via {locator_type}: {suggestion}"
                )
                break

        bus.emit(
            EventType.HEALING_COMPLETE,
            {"success": success, "recovered": recovered_selector},
        )
        return {
            "tc_id": tc_id,
            "original_selector": original_selector,
            "tried_locators": tried_locators,
            "recovered_selector": recovered_selector,
            "success": success,
            "confidence": confidence,
        }
