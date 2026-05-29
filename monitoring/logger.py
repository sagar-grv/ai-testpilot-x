"""Loguru-based structured logger."""
import sys
from loguru import logger as _logger
from config import settings

_logger.remove()
_logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> — <level>{message}</level>",
    colorize=True,
)
_logger.add(
    "execution/artifacts/logs/testpilot.log",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
)

def get_logger(name: str):
    return _logger.bind(module=name)
