from langchain_openai import ChatOpenAI

from app.config.settings import get_settings
from app.providers.base_provider import BaseLLMProvider


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self):
        settings = get_settings()
        self._model = ChatOpenAI(
            model=settings.minimax_model,
            openai_api_key=settings.minimax_api_key,
            openai_api_base=settings.minimax_base_url,
            temperature=0.3,
            streaming=True,
        )

    def get_model(self) -> ChatOpenAI:
        return self._model

    async def chat(self, messages: list[dict], stream: bool = False):
        if stream:
            return self._model.astream(messages)
        return await self._model.ainvoke(messages)

    def with_structured_output(self, schema, method: str = "function_calling"):
        return self._model.with_structured_output(schema, method=method)


_provider: BaseLLMProvider | None = None


def get_llm_provider() -> BaseLLMProvider:
    global _provider
    if _provider is None:
        _provider = OpenAICompatibleProvider()
    return _provider
