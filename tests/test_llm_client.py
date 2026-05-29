from unittest.mock import patch

def test_llm_client_imports():
    from core.llm_client import LLMClient
    assert LLMClient is not None

def test_llm_client_gemini_provider():
    from core.llm_client import LLMClient
    c = LLMClient(provider="gemini")
    assert c.provider == "gemini"

def test_llm_client_generate_calls_model():
    from core.llm_client import LLMClient
    with patch("models.gemini.GeminiModel.generate", return_value="test response"):
        c = LLMClient(provider="gemini")
        result = c.generate("Hello")
        assert result == "test response"

def test_llm_client_retries_on_failure():
    from core.llm_client import LLMClient
    call_count = 0
    def flaky(prompt):
        nonlocal call_count
        call_count += 1
        raise RuntimeError("API error")
    with patch("models.gemini.GeminiModel.generate", side_effect=flaky):
        c = LLMClient(provider="gemini", max_retries=2)
        try:
            c.generate("Hello")
        except RuntimeError:
            pass
    assert call_count == 2
