"""Mock LLM provider for testing without real API keys."""

from app.providers.base_provider import BaseLLMProvider


class MockProvider(BaseLLMProvider):
    def __init__(self, responses: dict | None = None):
        self.responses = responses or {}
        self.call_count = 0

    def get_model(self):
        return self

    async def chat(self, messages: list[dict], stream: bool = False):
        self.call_count += 1
        response = self.responses.get("chat", "Mock response")
        if stream:

            async def _stream():
                for char in response:
                    yield type("Chunk", (), {"content": char})()

            return _stream()
        return response

    def with_structured_output(self, schema, method: str = "function_calling"):
        return self
