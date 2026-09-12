import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_knowledge_documents_and_filtering(client: TestClient):
    token = get_auth_token(client)
    
    # 1. List all documents
    res = client.get(
        "/api/v1/ai/knowledge/documents",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) >= 5
    formats = [d["file_format"] for d in docs]
    assert "PDF" in formats
    assert "DOCX" in formats
    assert "MARKDOWN" in formats

    # 2. Filter by department
    res_sec = client.get(
        "/api/v1/ai/knowledge/documents?department=SECURITY",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_sec.status_code == 200
    sec_docs = res_sec.json()
    assert all(d["department"] == "SECURITY" for d in sec_docs)


def test_create_and_retrieve_document_metadata(client: TestClient):
    token = get_auth_token(client)
    
    create_payload = {
        "title": "Enterprise AI Governance & Model Risk Framework",
        "file_name": "AI_Governance_Framework_2026.pdf",
        "original_filename": "AI_Governance_Framework_2026.pdf",
        "file_format": "PDF",
        "file_size_bytes": 1850000,
        "mime_type": "application/pdf",
        "department": "EXECUTIVE",
        "category": "POLICY_GOVERNANCE",
        "tags": ["ai-governance", "xai", "risk-management"],
        "author": "AI Ethics Committee",
        "version": "v1.0",
        "summary_text": "Risk boundaries, explainability compliance, and algorithmic bias audit protocols.",
    }
    
    create_res = client.post(
        "/api/v1/ai/knowledge/documents",
        json=create_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_res.status_code == 201
    created_doc = create_res.json()
    doc_id = created_doc["id"]
    assert created_doc["document_sha256"] is not None
    assert len(created_doc["document_sha256"]) == 64

    # Retrieve by ID
    get_res = client.get(
        f"/api/v1/ai/knowledge/documents/{doc_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Enterprise AI Governance & Model Risk Framework"


def test_update_document_metadata(client: TestClient):
    token = get_auth_token(client)
    
    # Get first document
    res = client.get("/api/v1/ai/knowledge/documents", headers={"Authorization": f"Bearer {token}"})
    doc_id = res.json()[0]["id"]

    # Patch version and tags
    patch_res = client.patch(
        f"/api/v1/ai/knowledge/documents/{doc_id}",
        json={"version": "v2.5", "tags": ["updated", "certified"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["version"] == "v2.5"
    assert "updated" in patch_res.json()["tags"]


def test_knowledge_repository_stats(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/knowledge/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_documents"] >= 5
    assert data["total_storage_mb"] > 0
    assert "SECURITY" in data["department_counts"]
    assert "PDF" in data["format_counts"]
