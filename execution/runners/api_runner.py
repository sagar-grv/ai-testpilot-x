"""API test runner — executes HTTP tests against a real base URL."""
from __future__ import annotations
import asyncio
import time
import httpx
from schemas.api_test_schema import APITestResultSchema
from monitoring.logger import get_logger

log = get_logger(__name__)


async def run_api_test(base_url: str, test: APITestResultSchema) -> APITestResultSchema:
    """Execute one API test and return updated schema with actual results."""
    url = base_url.rstrip("/") + test.endpoint
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            method_fn = getattr(client, test.method.lower())
            kwargs = {}
            if test.body:
                kwargs["json"] = test.body
            resp = await method_fn(url, **kwargs)
        test.actual_status = resp.status_code
        test.response_body = resp.text[:2000]
        test.response_time_ms = (time.perf_counter() - start) * 1000
        test.passed = resp.status_code == test.expected_status
        log.info(f"API test {test.method} {test.endpoint} -> {resp.status_code} ({'PASS' if test.passed else 'FAIL'})")
    except Exception as e:
        test.response_time_ms = (time.perf_counter() - start) * 1000
        test.response_body = str(e)
        test.passed = False
        log.warning(f"API test {test.method} {test.endpoint} failed: {e}")
    return test


def run_api_test_sync(base_url: str, test: APITestResultSchema) -> APITestResultSchema:
    """Synchronous wrapper for Streamlit compatibility."""
    return asyncio.run(run_api_test(base_url, test))
