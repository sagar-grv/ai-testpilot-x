# CLI Reference

Complete reference for all `testpilot` commands and flags.

## Global flags

```
testpilot --help       Show help
testpilot --version    Show version
```

---

## `testpilot init`

Initialize a `testpilot.yaml` config file in the current directory.

```bash
testpilot init
```

**Interactive prompts:**

- Gemini API key
- Target application URL
- Execution mode (MOCK / LOCAL / GRID)
- Output directory

**Creates:** `testpilot.yaml` in the current working directory.

---

## `testpilot run`

Run the full 10-agent QA pipeline: analyze → generate → verify → execute → report.

```bash
testpilot run --story "User can login and checkout" [OPTIONS]
```

### Flags

| Flag | Short | Type | Required | Description |
|---|---|---|---|---|
| `--story` | `-s` | TEXT | Yes | Plain-English user story to test |
| `--url` | `-u` | TEXT | No | Target app URL (overrides `testpilot.yaml`) |
| `--config` | `-c` | PATH | No | Path to `testpilot.yaml` (default: auto-detect in cwd) |
| `--mode` | `-m` | TEXT | No | Execution mode: `MOCK` \| `LOCAL` \| `GRID` |
| `--output` | `-o` | PATH | No | Save full report JSON to this file |
| `--session` | | TEXT | No | Session ID (auto-generated if omitted) |

### Exit codes

<div class="tp-exit-codes">

| Code | Meaning | When |
|---|---|---|
| `0` | **GO** | All tests pass, no critical bugs |
| `1` | **GO WITH RISK** | High severity bugs found, non-critical failures |
| `2` | **NO GO** | Critical bugs, release blocked |

</div>

!!! note "CI/CD Integration"
    These exit codes work natively with GitHub Actions, GitLab CI, Jenkins, and any shell-based pipeline. A non-zero exit causes the CI job to fail.

### Examples

```bash
# Basic MOCK run
testpilot run --story "User can reset their password" --mode MOCK

# Against a live staging URL
testpilot run \
  --story "User can add items to cart and checkout" \
  --url https://staging.myapp.com \
  --mode LOCAL

# Save report JSON
testpilot run --story "Admin manages user accounts" --output report.json

# With explicit config file
testpilot run --story "..." --config ./ci/testpilot.yaml
```

---

## `testpilot analyze`

Generate test cases from a user story without executing anything.

```bash
testpilot analyze --story "User can filter search results" [OPTIONS]
```

### Flags

| Flag | Short | Type | Required | Description |
|---|---|---|---|---|
| `--story` | `-s` | TEXT | Yes | User story to analyze |
| `--output` | `-o` | PATH | No | Save test cases JSON to this file |

### Output

Prints a Rich table with:

- Test case ID, title, type (UI/API/edge)
- Priority (critical/high/medium/low)
- Coverage modules
- Steps summary

### Example

```bash
testpilot analyze --story "User can filter and sort product listings"
testpilot analyze --story "Payment flow with 3D Secure" --output test_cases.json
```

---

## `testpilot bugs`

Analyze an error log or stack trace using AI + RAG correlation.

```bash
testpilot bugs --log "NoSuchElementException: #login-btn" [OPTIONS]
```

### Flags

| Flag | Short | Type | Required | Description |
|---|---|---|---|---|
| `--log` | `-l` | TEXT | Yes | Error text, stack trace, or path to a log file |

### Input formats

```bash
# Inline stack trace
testpilot bugs --log "NoSuchElementException: Unable to locate element: #submit"

# Log file path
testpilot bugs --log ./test-output.log

# Piped from another command
cat error.log | testpilot bugs --log -
```

### Output

- Bug severity (critical / high / medium / low)
- Root cause analysis
- Similar bugs from RAG knowledge base
- Fix suggestion with code hint
- Affected component

---

## `testpilot report`

Generate a GO/NO GO release decision from an existing results JSON file.

```bash
testpilot report RESULTS_FILE [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `RESULTS_FILE` | Yes | Path to a JSON results file (from `testpilot run --output`) |

### Flags

| Flag | Short | Type | Required | Description |
|---|---|---|---|---|
| `--output` | `-o` | PATH | No | Save release report JSON to this file |

### Example

```bash
testpilot report test_results.json
testpilot report test_results.json --output release_report.json
```

---

## `testpilot dashboard`

Launch the Streamlit visual dashboard.

```bash
testpilot dashboard [OPTIONS]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--port` | INT | 8501 | Port to run the dashboard on |

### Example

```bash
testpilot dashboard
testpilot dashboard --port 8080
```

!!! info "Requires ui extras"
    The dashboard requires `pip install ai-testpilot-x[ui]` (includes Streamlit, Plotly, streamlit-agraph).

---

## Environment variables

All config values can be set via environment variables:

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `EXECUTION_MODE` | `MOCK` \| `LOCAL` \| `GRID` | `MOCK` |
| `DB_URL` | SQLAlchemy database URL | `sqlite:///.testpilot/testpilot.db` |
| `CHROMA_PATH` | ChromaDB storage directory | `.testpilot/chroma_db` |
| `OUTPUT_DIR` | Report output directory | `.testpilot/reports` |
| `LOG_LEVEL` | Logging verbosity | `WARNING` |
| `TARGET_URL` | Default target application URL | None |
