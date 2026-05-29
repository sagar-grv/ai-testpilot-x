"""ExecutionAgent — HITL gate + test runner (LOCAL/MOCK/GRID)."""
from __future__ import annotations
import random
from agents.base_agent import BaseAgent
from schemas.execution_schema import ExecutionSchema
from schemas.test_result_schema import TestResultSchema
from core.event_bus import bus, EventType
from storage.db import get_session
from storage.models.trust_domains import TrustDomain
from monitoring.logger import get_logger

log = get_logger(__name__)

MOCK_ERRORS = [
    "NoSuchElementException: Unable to locate element: #login-btn",
    "AssertionError: Expected status 200, got 404",
    "TimeoutException: Element not clickable after 10 seconds: .checkout-btn",
    "ElementClickInterceptedException: Other element obscures: #submit",
    "StaleElementReferenceException: Element is no longer in DOM",
]


class ExecutionAgent(BaseAgent):
    agent_name = "ExecutionAgent"

    def prepare_execution_plan(self, scripts: dict, target_url: str) -> str:
        lines = [f"Execution Plan — Target: {target_url}", f"Test scripts: {len(scripts)}"]
        for tc_id in scripts:
            lines.append(f"  - {tc_id}")
        return "\n".join(lines)

    def check_trust_domain(self, domain: str) -> bool:
        """Return True if domain is in trust_domains table."""
        try:
            session = get_session()
            result = session.query(TrustDomain).filter_by(domain=domain).first()
            session.close()
            return result is not None
        except Exception as e:
            self.log.warning(f"check_trust_domain error: {e}")
            return False

    def add_trust_domain(self, domain: str) -> None:
        """Persist domain to trust_domains table."""
        try:
            session = get_session()
            if not session.query(TrustDomain).filter_by(domain=domain).first():
                session.add(TrustDomain(domain=domain))
                session.commit()
            session.close()
            self.log.info(f"Trust domain added: {domain}")
        except Exception as e:
            self.log.warning(f"add_trust_domain error: {e}")

    def run(self, mode: str, scripts: dict, target_url: str, approved: bool) -> ExecutionSchema:
        if not approved:
            raise ValueError("Execution not approved. User must approve via HITL gate.")
        if mode == "MOCK":
            return self._run_mock(scripts)
        elif mode == "LOCAL":
            return self._run_local(scripts, target_url)
        elif mode == "GRID":
            return self._run_grid(scripts, target_url)
        else:
            raise ValueError(f"Unknown execution mode: {mode}")

    def _run_mock(self, scripts: dict) -> ExecutionSchema:
        """Return fake results with ~80% pass rate."""
        results = []
        for tc_id in scripts:
            passed = random.random() > 0.2
            results.append(TestResultSchema(
                tc_id=tc_id,
                status="PASS" if passed else "FAIL",
                duration_ms=random.uniform(500, 3000),
                error_message="" if passed else random.choice(MOCK_ERRORS),
            ))
        passed_count = sum(1 for r in results if r.status == "PASS")
        schema = ExecutionSchema(mode="MOCK", results=results, total=len(results),
                                 passed=passed_count, failed=len(results) - passed_count)
        bus.emit(EventType.EXECUTION_COMPLETE, {"total": schema.total, "failed": schema.failed})
        return schema

    def _run_local(self, scripts: dict, target_url: str) -> ExecutionSchema:
        from execution.runners.selenium_runner import run_test
        from config import settings
        results = []
        for tc_id, code in scripts.items():
            result = run_test(tc_id, code, target_url, headless=settings.SELENIUM_HEADLESS)
            results.append(result)
        passed_count = sum(1 for r in results if r.status == "PASS")
        screenshots = [r.screenshot_path for r in results if r.screenshot_path]
        schema = ExecutionSchema(mode="LOCAL", results=results, total=len(results),
                                 passed=passed_count, failed=len(results) - passed_count,
                                 screenshots=screenshots)
        bus.emit(EventType.EXECUTION_COMPLETE, {"total": schema.total, "failed": schema.failed})
        return schema

    def _run_grid(self, scripts: dict, target_url: str) -> ExecutionSchema:
        from execution.grids.selenium_grid import get_grid_driver
        from config import settings
        import time
        results = []
        for tc_id, code in scripts.items():
            start = time.perf_counter()
            driver = None
            try:
                driver = get_grid_driver(settings.SELENIUM_GRID_URL, headless=True)
                driver.get(target_url)
                namespace: dict = {}
                exec(compile(code, "<selenium_script>", "exec"), namespace)
                namespace[f"test_{tc_id}"](driver)
                duration_ms = (time.perf_counter() - start) * 1000
                results.append(TestResultSchema(tc_id=tc_id, status="PASS", duration_ms=duration_ms))
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                results.append(TestResultSchema(tc_id=tc_id, status="FAIL", duration_ms=duration_ms, error_message=str(e)))
            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass
        passed_count = sum(1 for r in results if r.status == "PASS")
        schema = ExecutionSchema(mode="GRID", results=results, total=len(results),
                                 passed=passed_count, failed=len(results) - passed_count)
        bus.emit(EventType.EXECUTION_COMPLETE, {"total": schema.total, "failed": schema.failed})
        return schema
