# ExecutionAgent

Runs test scripts in MOCK / LOCAL / GRID mode and manages the Human-in-the-Loop approval gate.

## Responsibility

The only agent that actually executes code. Manages the execution environment, HITL gate, trust domains, and collects raw results.

## Input

```python
class ExecutionInput(BaseModel):
    selenium_scripts: list[SeleniumScript]
    api_tests: list[APITest]
    execution_mode: str    # MOCK | LOCAL | GRID
    target_url: str
    approval_fn: Callable[[], bool] | None
```

## Output

```python
class ExecutionResult(BaseModel):
    test_case_id: str
    status: str            # "passed" | "failed" | "skipped" | "error"
    duration_ms: int
    error_message: str | None
    screenshot_path: str | None
    locator_used: str | None
    healing_triggered: bool
```

## HITL gate

Before executing, the agent calls `approval_fn()` if provided:

```python
# In CLI: approval_fn = None → auto-approve
# In Streamlit: approval_fn = lambda: st.session_state.get("hitl_approved", False)
# In Python API: user-supplied callback

if self.approval_fn is not None:
    approved = self.approval_fn({"test_cases": test_cases, "mode": mode})
    if not approved:
        return ExecutionResult(status="skipped", reason="HITL rejected")
```

## Execution modes

=== "MOCK"

    The AI simulates test execution and generates realistic results based on the test steps. No real browser or HTTP calls. Used in CI/cloud environments.

    ```python
    # Gemini generates: would this test pass or fail given these steps?
    # Returns plausible pass/fail with realistic error messages for failures
    ```

=== "LOCAL"

    Launches a real Chrome browser via `webdriver-manager`. Requires Chrome installed locally.

    ```python
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager

    driver = webdriver.Chrome(ChromeDriverManager().install())
    ```

=== "GRID"

    Connects to a Selenium Grid hub. Enables parallel execution across multiple browsers.

    ```python
    driver = webdriver.Remote(
        command_executor=settings.selenium_grid_url,
        options=chrome_options
    )
    ```

## Trust domains

The agent maintains a `trust_domains` table. URLs added to trusted domains bypass certain safety checks. Useful for staging environments.

```bash
# Add a trust domain
testpilot run --story "..." --url https://staging.internal.myapp.com
# staging.internal.myapp.com is auto-added to trust_domains
```
