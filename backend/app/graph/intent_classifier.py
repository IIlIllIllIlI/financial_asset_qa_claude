"""LLM-based intent classification."""

from pydantic import BaseModel
from typing import Literal

from app.utils.logger import setup_logger

logger = setup_logger("graph.intent")


class IntentResult(BaseModel):
    intent: Literal["market", "rag", "hybrid", "unsupported"]


async def classify_intent(query: str, llm_provider, intent_prompt: str) -> IntentResult:
    """Classify user query intent using LLM function_calling."""
    structured_llm = llm_provider.get_model().with_structured_output(
        IntentResult, method="function_calling"
    )
    result = await structured_llm.ainvoke(
        intent_prompt.replace("{user_query}", query)
    )
    if isinstance(result, IntentResult):
        return result
    return IntentResult(intent="market")
