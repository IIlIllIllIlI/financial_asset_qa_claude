"""Text processing utilities."""

import re


def strip_thinking(text: str) -> str:
    """Remove <think>...</think> tags from reasoning model output."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()
