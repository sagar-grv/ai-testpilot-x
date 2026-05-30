# SeleniumAgent

Generates executable Python Selenium 4 scripts for each UI test case.

## Responsibility

Converts structured test case steps into runnable Selenium WebDriver code with robust, multi-strategy locators.

## Input

```python
class SeleniumInput(BaseModel):
    test_cases: list[TestCase]   # type == "ui" only
    target_url: str
```

## Output

```python
class SeleniumScript(BaseModel):
    test_case_id: str
    filename: str        # "test_tc001_login.py"
    code: str            # full Python source
    locators: list[Locator]

class Locator(BaseModel):
    element: str         # "login button"
    strategies: dict     # {"id": "login-btn", "css": ".auth-form button[type=submit]"}
```

## Generated code structure

Each generated script is a `pytest`-compatible file:

```python
# test_tc001_google_oauth_login.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestGoogleOAuthLogin:
    """TC-001: Happy path: Google OAuth login and dashboard redirect"""

    def test_login_and_redirect(self, driver):
        driver.get("https://your-app.com/login")

        # Click Google Sign In
        sign_in_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "google-signin"))
        )
        sign_in_btn.click()

        # Complete OAuth (handled by browser)
        WebDriverWait(driver, 30).until(
            EC.url_contains("/dashboard")
        )

        # Assert redirect
        assert "/dashboard" in driver.current_url
        assert driver.find_element(By.CSS_SELECTOR, "[data-testid='user-menu']").is_displayed()
```

## Locator strategy

For each element, Gemini generates multiple locator strategies in priority order:

```
1. data-testid  (most stable — semantic, unlikely to change)
2. id           (stable if not auto-generated)
3. name         (for form inputs)
4. CSS selector (structural fallback)
5. XPath        (last resort)
```

All strategies are stored in the `Locator` object. At runtime, `HealingAgent` uses them as fallbacks if the primary locator fails.
