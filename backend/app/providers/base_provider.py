from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    @abstractmethod
    def get_model(self):
        pass

    @abstractmethod
    async def chat(self, messages: list[dict], stream: bool = False):
        pass

    @abstractmethod
    def with_structured_output(self, schema, method: str = "function_calling"):
        pass
