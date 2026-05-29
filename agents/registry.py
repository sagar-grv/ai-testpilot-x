"""AgentRegistry — pluggable agent routing."""
from __future__ import annotations
from monitoring.logger import get_logger

log = get_logger(__name__)


class AgentRegistry:
    _registry: dict[str, type] = {}

    @classmethod
    def register(cls, name: str, agent_class: type) -> type:
        cls._registry[name] = agent_class
        log.debug(f"AgentRegistry: registered {name} -> {agent_class.__name__}")
        return agent_class

    @classmethod
    def get(cls, name: str) -> type | None:
        return cls._registry.get(name)

    @classmethod
    def list_agents(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()
