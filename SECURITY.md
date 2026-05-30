# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | Active — security fixes backported |
| < 1.0   | Not supported |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Report security issues privately to: **sagar-grv** via [GitHub Security Advisories](https://github.com/sagar-grv/ai-testpilot-x/security/advisories/new)

We will respond within 72 hours and aim to release a patch within 14 days for critical issues.

---

## Threat Model

AI TestPilot X is a developer CLI tool and Streamlit dashboard. It is designed to run:

- **Locally** on a developer's machine (primary use case)
- **In CI/CD** pipelines (GitHub Actions, GitLab CI) with `EXECUTION_MODE=MOCK`
- **Streamlit Cloud** demo deployment with `EXECUTION_MODE=MOCK` (no real browser)

It is **not** designed to be deployed as a multi-tenant public web service. The Streamlit dashboard is single-user by design.

---

## Security Controls Implemented

### Input Validation
- All user-supplied text (user stories, error logs) is sanitized in `agents/base_agent.py:_sanitize_input()` before LLM embedding: max length enforced (15,000 chars for stories, 20,000 for logs), null bytes and control characters stripped.
- CLI commands enforce input length limits before calling agents.
- Streamlit text areas use `max_chars` constraints.

### LLM-Generated Code Execution
- All LLM-generated Selenium code is **AST-validated** in `core/code_validator.py` before `exec()`.
- The validator blocks: dangerous module imports (`os`, `subprocess`, `socket`, `shutil`, etc.), unsafe builtins (`eval`, `exec`, `open`, `__import__`), and dunder attribute access.
- The `exec()` calls in `execution/runners/selenium_runner.py` and `agents/execution_agent.py` carry `# nosec B102` annotations confirming the AST validation guard.

### XSS Prevention
- All user-supplied and LLM-generated text embedded in Streamlit `unsafe_allow_html=True` blocks is HTML-escaped with `html.escape()`.
- This covers: bug root cause, fix suggestions, error messages, recommendation text, filenames, and collection names.

### File Upload Security
- Server-side file size limit: 10 MB per file (enforced in `pages/08_knowledge_base.py`).
- Path traversal prevention: `Path(f.name).name` strips all directory components from uploaded filenames before writing to temp dir.

### Secrets Management
- API keys must be stored in environment variables or `.env` (gitignored).
- `.env` is in `.gitignore` — never committed.
- GitHub Actions uses repository secrets (`${{ secrets.GEMINI_API_KEY }}`).
- Streamlit Cloud uses the Secrets UI (not committed to source).

### Dependency Security
- `pip-audit` runs in CI on every push to scan for known CVEs.
- `bandit` runs in CI at MEDIUM severity threshold.
- All production dependencies have upper-bound version pins to prevent silent breaking upgrades.

### Logging
- File log level respects `LOG_LEVEL` setting (default: `WARNING`).
- No API keys, user data, or prompt content is logged at any level.
- LLM prompt content is never written to log files.

---

## Known Accepted Risks

### CVE-2026-45829 — chromadb Critical (CVSS 10.0)
**Why accepted:** This vulnerability requires a running ChromaDB HTTP server to be network-reachable. AI TestPilot X uses ChromaDB exclusively in **local embedded mode** (no HTTP server, no network socket exposed). The vulnerable `/api/v2/.../collections` endpoint is never created. No patch is available as of v1.0.0.

**Mitigation:** `trust_remote_code` is not set to `True` anywhere in the codebase. All ChromaDB collections are created with default settings.

### CVE-2026-41481 — langchain-text-splitters SSRF (CVSS 6.5)
**Why accepted:** The vulnerable method `HTMLHeaderTextSplitter.split_text_from_url()` is never called in this project. `langchain-text-splitters` is a transitive dependency pulled in by LangChain. Upgrading to 1.1.2 (the fix) breaks compatibility with the LangChain 0.3.x API this project uses.

**Mitigation:** The SSRF path requires explicit user code calling `split_text_from_url()` with an attacker-controlled URL. This is never done.

### exec() with AST validation
**Why accepted:** Selenium test execution requires running LLM-generated Python code. Pure static code generation without execution would eliminate the QA value proposition.

**Mitigation:** All generated code passes AST validation in `core/code_validator.py` before `exec()`. The validator blocks dangerous module imports and unsafe builtins. Generated code runs in an isolated namespace dict, not the global namespace.

---

## CI Security Gates

Every push to `master`/`main` runs:

```yaml
# .github/workflows/testpilot-ci.yml
- name: Security scan (bandit)
  run: bandit -r . --severity-level medium --confidence-level high

- name: Dependency audit (pip-audit)
  run: pip-audit --requirement requirements.txt
```

Both gates must pass for CI to succeed.
