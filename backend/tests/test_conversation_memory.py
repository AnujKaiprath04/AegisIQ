import pytest
from fastapi.testclient import TestClient
from app.memory_service.summarizer import ConversationSummarizer
from app.memory_service.types import ChatMessageRecord


def get_auth_token(client: TestClient, email: str = "executive@aegisiq.com", password: str = "Exec@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_conversation_summarizer_logic():
    messages = [
        ChatMessageRecord(message_id="1", role="user", content="What is our Q1 ARR?", tokens=6, timestamp="2026-08-31T00:00:00Z"),
        ChatMessageRecord(message_id="2", role="assistant", content="Current ARR is $24.8M.", tokens=7, timestamp="2026-08-31T00:00:01Z"),
    ]
    summary = ConversationSummarizer.summarize_history(messages)
    assert "Executive Dialogue Summary" in summary
    assert "Q1 ARR" in summary


def test_session_lifecycle_and_messages(client: TestClient):
    token = get_auth_token(client)
    
    # 1. Create Session
    create_res = client.post(
        "/api/v1/ai/memory/sessions",
        json={"title": "Q3 Board Strategy Dialogue"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_res.status_code == 201
    session_data = create_res.json()
    session_id = session_data["session_id"]
    assert session_data["title"] == "Q3 Board Strategy Dialogue"

    # 2. Append Message Turn 1 (User)
    msg1_res = client.post(
        f"/api/v1/ai/memory/sessions/{session_id}/messages",
        json={"role": "user", "content": "How are our ARR targets tracking against the forecast?", "intent": "BUSINESS_ANALYTICS"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert msg1_res.status_code == 200
    assert msg1_res.json()["tokens"] > 0

    # 3. Append Message Turn 2 (Assistant)
    msg2_res = client.post(
        f"/api/v1/ai/memory/sessions/{session_id}/messages",
        json={"role": "assistant", "content": "ARR is pacing at $24.8M (+18.4% YoY) exceeding targets by 12.7%.", "intent": "EXECUTIVE_INSIGHT"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert msg2_res.status_code == 200

    # 4. Get Session Detail
    get_res = client.get(
        f"/api/v1/ai/memory/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["total_messages"] == 2

    # 5. Get Context Window
    window_res = client.get(
        f"/api/v1/ai/memory/sessions/{session_id}/context-window?window_size=5&max_tokens=1024",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert window_res.status_code == 200
    assert len(window_res.json()["recent_messages"]) == 2
    assert window_res.json()["total_context_tokens"] > 0

    # 6. Trigger Rolling Summarization
    sum_res = client.post(
        f"/api/v1/ai/memory/sessions/{session_id}/summarize",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert sum_res.status_code == 200
    assert "Executive Dialogue Summary" in sum_res.json()["rolling_summary"]

    # 7. Delete Session
    del_res = client.delete(
        f"/api/v1/ai/memory/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] is True
