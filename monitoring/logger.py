"""monitoring/logger.py — Loguru-based structured logger with safe path handling."""
import sys
from pathlib import Path
from loguru import logger as _logger

# Remove default handler
_logger.remove()

# ── Determine log level ───────────────────────────────────────────────────────
def _get_log_level() -> str:
    try:
        from config import settings
        return settings.LOG_LEVEL
    except Exception:
        return "WARNING"

LOG_LEVEL = _get_log_level()

# ── Console handler ───────────────────────────────────────────────────────────
_logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    format=(
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan> — <level>{message}</level>"
    ),
    colorize=True,
)

# ── File handler (only if a writable directory exists) ────────────────────────
def _setup_file_handler() -> None:
    """Set up a rotating file log. Tries .testpilot/logs/ first, then falls back."""
    candidates = [
        Path.cwd() / ".testpilot" / "logs" / "testpilot.log",
        Path(__file__).parent.parent / "execution" / "artifacts" / "logs" / "testpilot.log",
    ]
    for log_path in candidates:
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            _logger.add(
                str(log_path),
                level="DEBUG",
                rotation="10 MB",
                retention="7 days",
                compression="zip",
                format="{time} | {level} | {name}:{line} — {message}",
            )
            return
        except (PermissionError, OSError):
            continue


_setup_file_handler()


def get_logger(name: str):
    """Return a logger bound to the given module name."""
    return _logger.bind(module=name)
