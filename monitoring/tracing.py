"""LangSmith tracing setup."""

import os
from config import settings
from monitoring.logger import get_logger

log = get_logger(__name__)


def configure_tracing():
    if not settings.LANGSMITH_TRACING or not settings.LANGSMITH_API_KEY:
        log.debug("LangSmith tracing disabled")  # debug level — silent at WARNING
        return
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
    log.info(f"LangSmith tracing enabled -> project={settings.LANGSMITH_PROJECT}")
