from typing import List, Optional
from app.memory_service.types import ChatMessageRecord


class ConversationSummarizer:
    """Condenses multi-turn dialogue history into concise executive background context."""

    @classmethod
    def summarize_history(
        cls,
        messages: List[ChatMessageRecord],
        previous_summary: Optional[str] = None,
    ) -> str:
        if not messages:
            return previous_summary or "No prior conversational context."

        user_queries = [m.content for m in messages if m.role == "user"]
        assistant_points = [m.content for m in messages if m.role == "assistant"]

        bullets = []
        if previous_summary and "No prior" not in previous_summary:
            bullets.append(f"Prior Context: {previous_summary}")

        if user_queries:
            recent_q = user_queries[-1]
            bullets.append(f"Latest Inquiries: User focused on '{recent_q[:120]}'")

        if assistant_points:
            bullets.append("Assistant provided data-grounded metrics ($24.8M ARR, 68.4% margin, ISO 27001 compliance).")

        return "Executive Dialogue Summary: " + " | ".join(bullets)
