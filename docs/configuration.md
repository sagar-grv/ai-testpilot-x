# Configuration Reference

All configuration for AI TestPilot X is read from three sources, in priority order:

1. **Environment variables** (highest priority)
2. **`testpilot.yaml`** in the current directory
3. **Streamlit secrets** (`secrets.toml` — Streamlit Cloud only)
4. **Defaults** (lowest priority)

## `testpilot.yaml`

Generate with `testpilot init`. Place in your project root.

```yaml
# testpilot.yaml

# --- Required ---
gemini_api_key: ${GEMINI_API_KEY}     # reads env var; or paste key directly

# --- Execution ---
execution_mode: MOCK                   # MOCK | LOCAL | GRID
target_url: https://your-app.com       # default target URL for Selenium tests
selenium_grid_url: ""                  # only needed for GRID mode

# --- Storage ---
db_url: sqlite:///.testpilot/testpilot.db
chroma_path: .testpilot/chroma_db
output_dir: .testpilot/reports

# --- Logging ---
log_level: WARNING                     # DEBUG | INFO | WARNING | ERROR
log_path: .testpilot/logs/testpilot.log

# --- LangSmith (optional tracing) ---
langsmith_api_key: ""                  # leave empty to disable
langsmith_project: ai-testpilot-x
```

## All configuration keys

### Core

| Key | Type | Default | Description |
|---|---|---|---|
| `gemini_api_key` | `str` | Required | Google Gemini API key |
| `execution_mode` | `str` | `MOCK` | `MOCK` / `LOCAL` / `GRID` |
| `target_url` | `str` | `""` | Default target URL for Selenium |
| `selenium_grid_url` | `str` | `""` | Selenium Grid hub URL (GRID mode only) |

### Storage

| Key | Type | Default | Description |
|---|---|---|---|
| `db_url` | `str` | `sqlite:///.testpilot/testpilot.db` | SQLAlchemy DB URL |
| `chroma_path` | `str` | `.testpilot/chroma_db` | ChromaDB storage path |
| `output_dir` | `str` | `.testpilot/reports` | Report output directory |

### Logging

| Key | Type | Default | Description |
|---|---|---|---|
| `log_level` | `str` | `WARNING` | Loguru log level |
| `log_path` | `str` | `.testpilot/logs/testpilot.log` | Log file path |

### LangSmith

| Key | Type | Default | Description |
|---|---|---|---|
| `langsmith_api_key` | `str` | `""` | Leave empty to disable tracing |
| `langsmith_project` | `str` | `ai-testpilot-x` | LangSmith project name |

## Environment variables

Every config key has a corresponding environment variable (uppercase):

```bash
export GEMINI_API_KEY="AIzaSy..."
export EXECUTION_MODE="MOCK"
export TARGET_URL="https://staging.myapp.com"
export DB_URL="sqlite:///./testpilot.db"
export CHROMA_PATH="./.chroma"
export OUTPUT_DIR="./reports"
export LOG_LEVEL="WARNING"
export LANGSMITH_API_KEY=""
```

## `.env` file

For local development, create a `.env` file (gitignored by default):

```bash
# .env
GEMINI_API_KEY=AIzaSy...
EXECUTION_MODE=MOCK
TARGET_URL=http://localhost:3000
LOG_LEVEL=WARNING
```

## Streamlit Cloud

For Streamlit Cloud deployment, add secrets via **Settings → Secrets** (TOML format):

```toml
GEMINI_API_KEY = "AIzaSy..."
EXECUTION_MODE = "MOCK"
LOG_LEVEL = "WARNING"
```

!!! warning "Never commit secrets"
    The `.env` file is gitignored. Never paste your API key directly into `testpilot.yaml` and commit it.

## CI/CD environment variables

For GitHub Actions:

```yaml
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  EXECUTION_MODE: MOCK
  DB_URL: sqlite:///./testpilot_ci.db
  CHROMA_PATH: ./chroma_ci
```

Add `GEMINI_API_KEY` to your repo secrets: **Settings → Secrets and variables → Actions → New repository secret**.
