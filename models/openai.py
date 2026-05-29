from models.base_model import BaseModel
class OpenAIModel(BaseModel):
    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("OpenAI not implemented in V1")
    def is_available(self) -> bool:
        return False
