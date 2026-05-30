"""In-process metrics collector."""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AgentMetric:
    name: str
    runs: int = 0
    errors: int = 0
    total_latency_ms: float = 0.0
    latencies: List[float] = field(default_factory=list)

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.runs if self.runs else 0.0

    @property
    def error_rate(self) -> float:
        return self.errors / self.runs if self.runs else 0.0


class MetricsCollector:
    def __init__(self):
        self._agents: Dict[str, AgentMetric] = {}

    def record_run(self, agent_name: str, latency_ms: float, error: bool = False):
        if agent_name not in self._agents:
            self._agents[agent_name] = AgentMetric(name=agent_name)
        m = self._agents[agent_name]
        m.runs += 1
        m.total_latency_ms += latency_ms
        m.latencies.append(latency_ms)
        if error:
            m.errors += 1

    def get_all(self) -> Dict[str, AgentMetric]:
        return dict(self._agents)

    def reset(self):
        self._agents.clear()


metrics = MetricsCollector()


class timer:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.error = False
        self._start = 0.0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def mark_error(self):
        self.error = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (time.perf_counter() - self._start) * 1000
        metrics.record_run(
            self.agent_name, elapsed, error=self.error or exc_type is not None
        )
        return False
