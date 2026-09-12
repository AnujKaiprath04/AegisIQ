import pytest
from fastapi.testclient import TestClient
from app.rag_engine.query_processor import QueryUnderstandingEngine
from app.rag_engine.context_compressor import ContextCompressor


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_query_understanding_and_expansion():
    # 1. Security query
    sec_analysis = QueryUnderstandingEngine.analyze_and_expand("What are the ISO 27001 access control requirements?")
    assert sec_analysis["inferred_department"] == "SECURITY"
    assert sec_analysis["target_collection"] == "security_policies"
    assert len(sec_analysis["sub_queries"]) >= 2

    # 2. Finance query
    fin_analysis = QueryUnderstandingEngine.analyze_and_expand("Summarize our Q1 ARR and gross profit margin growth.")
    assert fin_analysis["inferred_department"] == "FINANCE"
    assert fin_analysis["target_collection"] == "financial_reports"


def test_context_compression_and_token_budget():
    raw_results = [
        {"id": "c1", "document": "ISO 27001 Access Control Policy.", "score": 0.92, "metadata": {"title": "ISO 27001", "department": "SECURITY"}},
        {"id": "c2", "document": "Irrelevant noise text.", "score": 0.35, "metadata": {"title": "Noise"}},
        {"id": "c3", "document": "Multi-factor authentication key enforcement.", "score": 0.88, "metadata": {"title": "ISO 27001", "department": "SECURITY"}},
    ]
    passages, citations = ContextCompressor.compress_and_rank(raw_results, min_relevance_threshold=0.50)
    assert len(passages) == 2
    assert len(citations) == 2
    assert citations[0].relevance_score >= 0.88
    assert citations[0].source_id == 1


def test_rag_pipeline_end_to_end_query(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/rag/query",
        json={
            "query": "What are our mandatory ISO 27001 access control and security protocols?",
            "collection_name": "enterprise_knowledge",
            "top_k": 3,
            "provider_type": "LOCAL_ENTERPRISE",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert len(data["answer"]) > 50
    assert data["confidence_score"] > 0.60
    assert data["retrieval_latency_ms"] > 0
    assert data["total_latency_ms"] > 0
    assert len(data["citations"]) > 0
    assert data["citations"][0]["document_title"] is not None


def test_rag_retrieval_debugging_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/rag/retrieve",
        json={
            "query": "What is our Q1 2026 ARR and gross profit margin?",
            "collection_name": "enterprise_knowledge",
            "top_k": 3,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["passages_count"] > 0
    assert len(data["citations"]) > 0


def test_rag_explain_query_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/rag/explain-query",
        json={"query": "Explain our cloud disaster recovery and failover SLA protocol."},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "target_collection" in data
    assert len(data["sub_queries"]) >= 1


def test_rag_telemetry(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/rag/telemetry",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["pipeline_status"] == "OPERATIONAL"
    assert data["average_confidence_score"] > 0.80
