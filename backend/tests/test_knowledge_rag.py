import io
import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_knowledge_documents(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/knowledge/documents",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    docs = res.json()
    assert isinstance(docs, list)
    assert len(docs) >= 3
    assert any("ISO 27001" in d["title"] for d in docs)
    assert any("Financial" in d["title"] for d in docs)
    assert any("SLA" in d["title"] for d in docs)


def test_get_document_detail_and_chunks(client: TestClient):
    token = get_auth_token(client)
    docs_res = client.get("/api/v1/knowledge/documents", headers={"Authorization": f"Bearer {token}"})
    doc_id = docs_res.json()[0]["id"]

    res = client.get(
        f"/api/v1/knowledge/documents/{doc_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    doc = res.json()
    assert doc["id"] == doc_id
    assert "chunks" in doc
    assert len(doc["chunks"]) > 0
    first_chunk = doc["chunks"][0]
    assert first_chunk["token_count"] > 0
    assert len(first_chunk["embedding_preview"]) > 0


def test_semantic_rag_query_execution(client: TestClient):
    token = get_auth_token(client)
    
    query_payload = {
        "query": "What is our guaranteed service availability uptime and disaster recovery RTO?",
        "top_k": 3,
    }
    res = client.post(
        "/api/v1/knowledge/query",
        json=query_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "99.9%" in data["answer"]
    assert "60 minutes" in data["answer"] or "RTO" in data["answer"]
    assert len(data["matched_citations"]) > 0
    assert data["top_similarity_score"] > 0.60
    assert data["matched_citations"][0]["document_title"] is not None


def test_upload_and_delete_knowledge_document(client: TestClient):
    token = get_auth_token(client)
    
    sample_text = (
        "Enterprise Data Retention Protocol 2026. All transactional database backups are retained for 7 years. "
        "Customer personally identifiable information must be anonymized within 30 days upon contract termination. "
        "Zero-knowledge encryption keys are rotated bi-weekly."
    )
    file_bytes = io.BytesIO(sample_text.encode("utf-8"))

    upload_res = client.post(
        "/api/v1/knowledge/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"title": "Data Retention & Anonymization Standard", "category": "POLICY"},
        files={"file": ("retention_policy.txt", file_bytes, "text/plain")},
    )
    assert upload_res.status_code == 201
    created_doc = upload_res.json()
    doc_id = created_doc["id"]
    assert created_doc["total_chunks"] >= 1

    # Delete
    del_res = client.delete(
        f"/api/v1/knowledge/documents/{doc_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_res.status_code == 200
