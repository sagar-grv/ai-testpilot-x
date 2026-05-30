# APIAgent

Generates HTTP test suites using `httpx` for API test cases, with full request/response assertions.

## Responsibility

Converts API test cases into executable `httpx`-based test scripts with auth headers, request bodies, and detailed response assertions.

## Input

```python
class APIInput(BaseModel):
    test_cases: list[TestCase]   # type == "api" only
    target_url: str
```

## Output

```python
class APITest(BaseModel):
    test_case_id: str
    filename: str
    code: str
    endpoints: list[str]
    method: str
    expected_status: int
```

## Generated code structure

```python
# test_tc004_csrf_validation.py
import pytest
import httpx

BASE_URL = "https://your-app.com"

class TestCSRFValidation:
    """TC-004: Security: CSRF token validation on OAuth callback"""

    def test_callback_requires_valid_csrf(self):
        """OAuth callback must reject requests without valid state parameter."""
        with httpx.Client() as client:
            # Attempt callback without CSRF state
            response = client.get(
                f"{BASE_URL}/auth/callback",
                params={"code": "valid_code", "state": "tampered_state"},
                follow_redirects=False,
            )
            assert response.status_code in (400, 403), \
                f"Expected 400/403 for invalid CSRF state, got {response.status_code}"

    def test_callback_accepts_valid_csrf(self, auth_session):
        """OAuth callback with valid state returns 302 to dashboard."""
        response = auth_session.get(
            f"{BASE_URL}/auth/callback",
            params={"code": "valid_code", "state": auth_session.csrf_state},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["location"]
```

## Execution

API tests run via `httpx` in `ExecutionAgent`. They work in all execution modes (`MOCK`, `LOCAL`, `GRID`) since they're HTTP-based, not browser-based.

In `MOCK` mode, the AI generates plausible response scenarios without hitting a real endpoint.
