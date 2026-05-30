import google.generativeai as genai
from config import settings
from models.base_model import BaseModel
from monitoring.logger import get_logger

log = get_logger(__name__)
_MODEL_NAME = "gemini-2.5-flash"


class GeminiModel(BaseModel):
    def __init__(self, model_name: str = _MODEL_NAME):
        self.model_name = model_name
        self._configured = False
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._model = genai.GenerativeModel(model_name)
            self._configured = True
        else:
            log.warning("GEMINI_API_KEY not set")
            self._model = None

    def is_available(self) -> bool:
        return self._configured and self._model is not None

    def generate(self, prompt: str, **kwargs) -> str:
        if not self.is_available():
            raise RuntimeError("GeminiModel not available. Set GEMINI_API_KEY.")
        log.debug(f"Gemini generate | prompt_len={len(prompt)}")
        response = self._model.generate_content(prompt)
        return response.text
