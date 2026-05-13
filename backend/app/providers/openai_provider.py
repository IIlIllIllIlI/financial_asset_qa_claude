import copy
import re

from langchain_openai import ChatOpenAI

from app.config.settings import get_settings
from app.providers.base_provider import BaseLLMProvider
from app.utils.text import strip_thinking


class _ThinkStrippedModel:
    """Wraps a LangChain ChatOpenAI model, stripping <think>...</think> from
    streaming and non-streaming outputs.  Structured-output paths
    (with_structured_output / function_calling) pass through unchanged."""

    def __init__(self, raw_model: ChatOpenAI):
        self._raw = raw_model
        self._stream_buffer = ""
        self._stream_emitted = 0
        self._events_buffer = ""
        self._events_emitted = 0

    # ── non-streaming ──────────────────────────────────────────────

    async def ainvoke(self, messages, **kwargs):
        result = await self._raw.ainvoke(messages, **kwargs)
        if hasattr(result, "content") and isinstance(result.content, str):
            result.content = strip_thinking(result.content)
        return result

    def invoke(self, messages, **kwargs):
        result = self._raw.invoke(messages, **kwargs)
        if hasattr(result, "content") and isinstance(result.content, str):
            result.content = strip_thinking(result.content)
        return result

    # ── streaming (astream) ────────────────────────────────────────

    async def astream(self, messages, **kwargs):
        self._stream_buffer = ""
        self._stream_emitted = 0
        async for chunk in self._raw.astream(messages, **kwargs):
            processed = self._process_stream_chunk(chunk)
            if processed is not None:
                yield processed

    # ── streaming (astream_events v2) ──────────────────────────────

    async def astream_events(self, messages, version="v2", **kwargs):
        self._events_buffer = ""
        self._events_emitted = 0
        async for event in self._raw.astream_events(messages, version=version, **kwargs):
            if event.get("event") == "on_chat_model_stream":
                processed = self._process_events_chunk(event)
                if processed is not None:
                    yield processed
            else:
                yield event

    # ── structured output – delegate to raw model ──────────────────

    def with_structured_output(self, schema, method: str = "function_calling"):
        return self._raw.with_structured_output(schema, method=method)

    # ── internal helpers ───────────────────────────────────────────

    @staticmethod
    def _strip(text: str) -> str:
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    def _process_stream_chunk(self, chunk):
        """Buffer chunk, strip think blocks, emit only clean new content."""
        content = chunk.content if hasattr(chunk, "content") else None
        if not content:
            return chunk  # non-content chunks pass through

        self._stream_buffer += content
        last_open = self._stream_buffer.rfind("<think>")
        last_close = self._stream_buffer.rfind("</think>")
        if last_open > last_close:
            return None  # unclosed <think>, wait for more

        cleaned = self._strip(self._stream_buffer)
        new_content = cleaned[self._stream_emitted:]
        if new_content:
            chunk.content = new_content
            self._stream_emitted = len(cleaned)
            self._stream_buffer = cleaned
            return chunk
        return None

    def _process_events_chunk(self, event):
        """Buffer astream_events chunk, strip think, emit clean events."""
        chunk = event["data"]["chunk"]
        content = chunk.content if hasattr(chunk, "content") else None
        if not content:
            return event

        self._events_buffer += content
        last_open = self._events_buffer.rfind("<think>")
        last_close = self._events_buffer.rfind("</think>")
        if last_open > last_close:
            return None

        cleaned = self._strip(self._events_buffer)
        new_content = cleaned[self._events_emitted:]
        if new_content:
            new_event = copy.deepcopy(event)
            new_event["data"]["chunk"].content = new_content
            self._events_emitted = len(cleaned)
            self._events_buffer = cleaned
            return new_event
        return None

    # ── attribute delegation ───────────────────────────────────────

    def __getattr__(self, name):
        return getattr(self._raw, name)


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self):
        settings = get_settings()
        raw = ChatOpenAI(
            model=settings.minimax_model,
            openai_api_key=settings.minimax_api_key,
            openai_api_base=settings.minimax_base_url,
            temperature=0.3,
            streaming=True,
        )
        self._model = _ThinkStrippedModel(raw)

    def get_model(self):
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
