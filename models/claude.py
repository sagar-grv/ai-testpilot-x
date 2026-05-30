from models.base_model import BaseModel


class ClaudeModel(BaseModel):
    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("Claude not implemented in V1")

    def is_available(self) -> bool:
        return False
