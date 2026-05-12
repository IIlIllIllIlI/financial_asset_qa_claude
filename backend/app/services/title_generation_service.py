"""Async session title generation service."""

from sqlalchemy.orm import Session

from app.providers.openai_provider import get_llm_provider
from app.repositories.session_repository import SessionRepository
from app.utils.prompt_loader import load_prompt
from app.utils.logger import setup_logger
from app.utils.text import strip_thinking

logger = setup_logger("services.title")


async def generate_and_update_title(
    session_id: str,
    user_query: str,
    response_content: str,
    db_session_factory,
):
    """Generate title via LLM and update session in DB (fire-and-forget)."""
    try:
        summary = response_content[:200] if response_content else user_query[:100]

        prompt_template = load_prompt("title/title_generation.txt")
        prompt = prompt_template.replace("{user_query}", user_query)
        prompt = prompt.replace("{response_summary}", summary)

        provider = get_llm_provider()
        model = provider.get_model()
        result = await model.ainvoke(prompt)

        title = result.content.strip() if hasattr(result, "content") else str(result).strip()
        title = strip_thinking(title)
        title = title[:15] if len(title) > 15 else title

        if not title:
            title = "新对话"

        db = db_session_factory()()
        try:
            repo = SessionRepository(db)
            repo.update_title(session_id, title)
            logger.info(f"Title updated for session {session_id}: {title}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Title generation failed for session {session_id}: {e}")
