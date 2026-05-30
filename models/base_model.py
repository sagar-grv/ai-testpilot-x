from abc import ABC, abstractmethod


class BaseModel(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str: ...

    @abstractmethod
    def is_available(self) -> bool: ...
