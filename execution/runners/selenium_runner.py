"""Selenium test runner — LOCAL mode execution."""

from __future__ import annotations
import time
from pathlib import Path
from schemas.test_result_schema import TestResultSchema
from monitoring.logger import get_logger

log = get_logger(__name__)
SCREENSHOTS_DIR = Path("execution/artifacts/screenshots")

# Module-level imports so they can be patched in tests
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    _SELENIUM_AVAILABLE = True
except ImportError:
    webdriver = None  # type: ignore[assignment]
    Service = None  # type: ignore[assignment]
    ChromeDriverManager = None  # type: ignore[assignment]
    _SELENIUM_AVAILABLE = False


def run_test(
    tc_id: str, code: str, target_url: str, headless: bool = True
) -> TestResultSchema:
    """Execute a generated Selenium test function. Returns TestResultSchema."""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not _SELENIUM_AVAILABLE or webdriver is None:
        return TestResultSchema(
            tc_id=tc_id,
            status="ERROR",
            duration_ms=0.0,
            error_message="Selenium not installed",
        )

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = None
    start = time.perf_counter()
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(target_url)

        namespace: dict = {}
        exec(compile(code, "<selenium_script>", "exec"), namespace)
        fn_name = f"test_{tc_id}"
        if fn_name not in namespace:
            raise ValueError(f"Function {fn_name} not found in generated code")
        namespace[fn_name](driver)

        duration_ms = (time.perf_counter() - start) * 1000
        log.info(f"Test {tc_id} PASSED in {duration_ms:.0f}ms")
        return TestResultSchema(tc_id=tc_id, status="PASS", duration_ms=duration_ms)

    except Exception as e:
        duration_ms = (time.perf_counter() - start) * 1000
        screenshot_path = ""
        if driver:
            try:
                from core.screenshot_utils import capture_screenshot

                ss_path = str(SCREENSHOTS_DIR / f"{tc_id}_failure.png")
                screenshot_path = capture_screenshot(driver, ss_path)
            except Exception:
                pass
        log.error(f"Test {tc_id} FAILED: {e}")
        return TestResultSchema(
            tc_id=tc_id,
            status="FAIL",
            duration_ms=duration_ms,
            error_message=str(e),
            screenshot_path=screenshot_path,
        )
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
