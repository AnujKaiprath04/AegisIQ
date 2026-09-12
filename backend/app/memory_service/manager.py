import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.memory_service.types import (
    ChatMessageRecord,
    ContextWindowPayload,
    SessionMemoryState,
)
from app.memory_service.summarizer import ConversationSummarizer

logger = logging.getLogger("aegisiq.memory_service")


class ConversationMemoryManager:
    """Orchestrates episodic chat history, sliding-window retention, and rolling summaries."""

    _sessions: Dict[str, SessionMemoryState] = {}

    @classmethod
    def _estimate_tokens(cls, text: str) -> int:
        return max(1, len(text.split()))

    @classmethod
    def create_session(
        cls,
        user_id: int,
        title: Optional[str] = None,
        custom_id: Optional[str] = None,
    ) -> SessionMemoryState:
        session_id = custom_id or f"session-{user_id}-{int(time.time())}"
        now_str = datetime.now(timezone.utc).isoformat()
        
        session = SessionMemoryState(
            session_id=session_id,
            user_id=user_id,
            title=title or "Executive Decision Session",
            created_at=now_str,
            updated_at=now_str,
            total_messages=0,
            total_tokens=0,
            rolling_summary=None,
            messages=[],
        )
        cls._sessions[session_id] = session
        logger.info(f"Initialized conversation memory session: {session_id}")
        return session

    @classmethod
    def list_sessions(cls, user_id: int) -> List[SessionMemoryState]:
        # Return sessions for the specific user (or seeded demo sessions)
        user_sessions = [s for s in cls._sessions.values() if s.user_id == user_id]
        if not user_sessions and not cls._sessions:
            # Seed default demo session
            demo = cls.create_session(user_id=user_id, title="Q1 2026 Executive Strategy Session", custom_id="session-demo-01")
            cls.append_message(demo.session_id, "user", "What is our current ARR and gross margin trajectory?", "BUSINESS_ANALYTICS")
            cls.append_message(demo.session_id, "assistant", "Current ARR is pacing at $24.8M (+18.4% YoY) with a 68.4% gross profit margin.", "BUSINESS_ANALYTICS")
            return [demo]
        return user_sessions

    @classmethod
    def get_session(cls, session_id: str) -> SessionMemoryState:
        session = cls._sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory session '{session_id}' not found.")
        return session

    @classmethod
    def append_message(
        cls,
        session_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
    ) -> ChatMessageRecord:
        session = cls._sessions.get(session_id)
        if not session:
            session = cls.create_session(user_id=1, custom_id=session_id)

        tokens = cls._estimate_tokens(content)
        msg_id = f"msg-{int(time.time())}-{len(session.messages) + 1}"
        msg = ChatMessageRecord(
            message_id=msg_id,
            role=role.lower(),
            content=content.strip(),
            tokens=tokens,
            timestamp=datetime.now(timezone.utc).isoformat(),
            intent=intent,
        )

        session.messages.append(msg)
        session.total_messages = len(session.messages)
        session.total_tokens += tokens
        session.updated_at = datetime.now(timezone.utc).isoformat()

        # Automatically update rolling summary if message count exceeds 8
        if len(session.messages) >= 8 and len(session.messages) % 4 == 0:
            cls.generate_summary(session_id)

        return msg

    @classmethod
    def get_context_window(
        cls,
        session_id: str,
        window_size: int = 10,
        max_tokens: int = 2048,
    ) -> ContextWindowPayload:
        session = cls.get_session(session_id)
        
        # Take recent K messages
        recent = session.messages[-window_size:] if len(session.messages) > window_size else session.messages
        
        # Enforce max token budget
        filtered = []
        token_count = 0
        for msg in reversed(recent):
            if token_count + msg.tokens > max_tokens and len(filtered) >= 2:
                break
            filtered.insert(0, msg)
            token_count += msg.tokens

        return ContextWindowPayload(
            session_id=session.session_id,
            rolling_summary=session.rolling_summary,
            recent_messages=filtered,
            total_context_tokens=token_count,
        )

    @classmethod
    def generate_summary(cls, session_id: str) -> str:
        session = cls.get_session(session_id)
        summary = ConversationSummarizer.summarize_history(session.messages, session.rolling_summary)
        session.rolling_summary = summary
        session.updated_at = datetime.now(timezone.utc).isoformat()
        return summary

    @classmethod
    def delete_session(cls, session_id: str) -> bool:
        if session_id in cls._sessions:
            del cls._sessions[session_id]
            logger.info(f"Deleted memory session: {session_id}")
            return True
        return False
