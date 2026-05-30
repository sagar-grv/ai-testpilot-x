"""
core/explain_engine.py — Meta-prompt for AI explainability.
Used on Pages 02, 03, 04, 05 via "Explain AI Decision" expanders.
"""

from __future__ import annotations
from monitoring.logger import get_logger

log = get_logger(__name__)

_EXPLAIN_PROMPT = """Explain in plain English why the AI made the following decision.
Be concise (2-3 sentences). Use non-technical language suitable for a business stakeholder.

Decision context:
{decision_context}

Explanation:"""


def explain_decision(decision_context: str) -> str:
    """Call Gemini to explain an agent decision in plain English."""
    try:
        from core.llm_client import LLMClient

        client = LLMClient(provider="gemini")
        prompt = _EXPLAIN_PROMPT.format(decision_context=decision_context)
        return client.generate(prompt)
    except Exception as e:
        log.warning(f"explain_decision failed: {e}")
        return "Explanation unavailable. Check your GEMINI_API_KEY configuration."
