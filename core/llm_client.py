"""Unified LLM client with retry logic."""
from __future__ import annotations
import time
from typing import Literal
from config import settings
from models.base_model import BaseModel
from monitoring.logger import get_logger

log = get_logger(__name__)
ProviderType = Literal["gemini", "openai", "claude"]

def _build_model(provider: ProviderType) -> BaseModel:
    if provider == "gemini":
        from models.gemini import GeminiModel
        return GeminiModel()
    elif provider == "openai":
        from models.openai import OpenAIModel
        return OpenAIModel()
    elif provider == "claude":
        from models.claude import ClaudeModel
        return ClaudeModel()
    raise ValueError(f"Unknown provider: {provider}")

class LLMClient:
    def __init__(self, provider: ProviderType = "gemini", max_retries: int | None = None):
        self.provider = provider
        self.max_retries = max_retries if max_retries is not None else settings.MAX_AGENT_RETRIES
        self._model: BaseModel = _build_model(provider)

    def generate(self, prompt: str, **kwargs) -> str:
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                log.debug(f"LLMClient.generate | provider={self.provider} | attempt={attempt}")
                return self._model.generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                log.warning(f"LLM generate failed | attempt={attempt}/{self.max_retries} | {e}")
                if attempt < self.max_retries:
                    time.sleep(1.0)
        raise last_error

    def is_available(self) -> bool:
        return self._model.is_available()
