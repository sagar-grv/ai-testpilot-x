"""Selenium Grid connector for remote execution."""

from __future__ import annotations
import httpx
from monitoring.logger import get_logger

log = get_logger(__name__)


def get_grid_driver(grid_url: str, headless: bool = True):
    """Connect to Selenium Grid hub, return Remote WebDriver."""
    from selenium import webdriver

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Remote(command_executor=grid_url, options=options)
    log.info(f"Connected to Selenium Grid: {grid_url}")
    return driver


def check_grid_health(grid_url: str) -> bool:
    """Return True if grid hub is reachable and responding."""
    try:
        r = httpx.get(f"{grid_url}/status", timeout=3.0)
        return r.status_code == 200
    except Exception as e:
        log.warning(f"Grid health check failed: {e}")
        return False
