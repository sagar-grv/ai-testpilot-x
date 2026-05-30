# HealingAgent

Self-heals broken Selenium locators using a 7-level fallback hierarchy. Patches failing tests automatically.

## Responsibility

When a Selenium test fails with a `NoSuchElementException`, HealingAgent attempts to recover the locator using progressively broader strategies — without requiring human intervention.

## Input

```python
class HealingInput(BaseModel):
    bugs: list[Bug]                     # only NoSuchElementException bugs
    selenium_scripts: list[SeleniumScript]
```

## Output

```python
class HealedLocator(BaseModel):
    test_case_id: str
    element: str                    # "login button"
    original_locator: str           # By.ID, "#google-signin"
    healed_locator: str             # By.CSS_SELECTOR, "[data-testid='google-signin-btn']"
    strategy_used: str              # "data-testid"
    confidence: float
    patched_script: str             # updated Python code
```

## The 7-level fallback hierarchy

```
Level 1  ID attribute            By.ID, "google-signin"
Level 2  name attribute          By.NAME, "google_login"
Level 3  data-testid             By.CSS, "[data-testid='google-signin-btn']"
Level 4  data-qa                 By.CSS, "[data-qa='login-google']"
Level 5  CSS selector            By.CSS, ".auth-buttons > button:first-child"
Level 6  XPath                   By.XPATH, "//button[contains(text(),'Sign in with Google')]"
Level 7  AI-generated            Gemini generates new locator from DOM snapshot
```

At each level, if the element is found, healing stops and the script is patched. The healed locator is stored in ChromaDB so future test runs start with the recovered locator.

## Level 7: AI locator generation

If all 6 standard strategies fail, HealingAgent captures a DOM snapshot and asks Gemini:

```
[DOM snapshot — truncated]
<div class="auth-container">
  <button class="btn-oauth" data-provider="google" aria-label="Continue with Google">
    <svg>...</svg>
    Continue with Google
  </button>
</div>

The test was looking for: "Google Sign In button" (original locator: #google-signin)
Generate a robust locator for this element.
```

Gemini returns: `By.CSS_SELECTOR, "button[data-provider='google']"`

## Patching

After healing, the script is updated in-place:

```python
# Before healing
sign_in_btn = driver.find_element(By.ID, "google-signin")

# After healing (Level 3: data-testid)
sign_in_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='google-signin-btn']")
# HEALED: original locator By.ID('google-signin') → By.CSS('[data-testid=...]')
```

The healed locator is embedded in ChromaDB so the next pipeline run starts with the working locator — no repeated healing needed.
