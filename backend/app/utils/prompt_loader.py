"""Prompt loading utility."""

from pathlib import Path

_PROMPT_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(relative_path: str) -> str:
    """Load a prompt template from prompts/ directory."""
    prompt_path = _PROMPT_DIR / relative_path
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")
