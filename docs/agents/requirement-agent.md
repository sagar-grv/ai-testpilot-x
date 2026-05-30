# RequirementAgent

Parses a plain-English user story into structured requirement modules with priority and risk classification.

## Responsibility

The first agent in the pipeline. Takes the raw user story and produces a structured breakdown that all downstream agents use as their foundation.

## Input

```python
class RequirementInput(BaseModel):
    story: str           # "User can log in with valid credentials"
    session_id: str
```

## Output

```python
class RequirementOutput(BaseModel):
    modules: list[RequirementModule]
    priority: str        # "critical" | "high" | "medium" | "low"
    risk_areas: list[str]
    scope_summary: str

class RequirementModule(BaseModel):
    id: str              # "REQ-001"
    name: str            # "Authentication"
    description: str
    acceptance_criteria: list[str]
    risk_level: str
    tags: list[str]
```

## What it does

1. Calls Gemini 2.5 Flash with `prompts/requirement_prompt.txt`
2. Queries ChromaDB `requirements` collection for similar past requirements (RAG context)
3. Extracts: module names, acceptance criteria, risk areas, priority
4. Stores parsed modules to SQLite `requirements` table
5. Embeds modules into ChromaDB for future sessions

## Prompt

The prompt instructs Gemini to:
- Break the story into logical functional modules (auth, checkout, data, etc.)
- Identify risk areas (e.g., payment handling = high risk)
- Generate acceptance criteria per module in Given/When/Then format
- Assign priority based on business impact

## Example

**Input:** `"User can log in with Google OAuth and be redirected to dashboard"`

**Output:**
```json
{
  "modules": [
    {
      "id": "REQ-001",
      "name": "OAuth Authentication",
      "description": "Google OAuth 2.0 login flow",
      "acceptance_criteria": [
        "Given user clicks 'Sign in with Google', When OAuth completes, Then user is logged in",
        "Given OAuth fails, When error occurs, Then user sees error message"
      ],
      "risk_level": "high",
      "tags": ["auth", "oauth", "security"]
    },
    {
      "id": "REQ-002",
      "name": "Post-login Redirect",
      "description": "Dashboard redirect after successful login",
      "acceptance_criteria": [
        "Given user logs in, When auth succeeds, Then user is redirected to /dashboard"
      ],
      "risk_level": "low",
      "tags": ["navigation", "redirect"]
    }
  ],
  "priority": "high",
  "risk_areas": ["OAuth token handling", "Session management"],
  "scope_summary": "Google OAuth login with post-auth dashboard redirect"
}
```
