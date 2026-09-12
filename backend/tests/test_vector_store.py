import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_and_create_collections(client: TestClient):
    token = get_auth_token(client)
    
    # 1. List collections
    list_res = client.get(
        "/api/v1/ai/vector/collections",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_res.status_code == 200
    collections = list_res.json()
    assert len(collections) >= 4
    names = [c["name"] for c in collections]
    assert "enterprise_knowledge" in names
    assert "security_policies" in names
    assert "financial_reports" in names

    # 2. Create custom collection
    create_res = client.post(
        "/api/v1/ai/vector/collections",
        json={
            "name": "custom_hr_runbooks",
            "dimensions": 384,
            "description": "HR and employee operational runbooks collection.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_res.status_code == 201
    assert create_res.json()["name"] == "custom_hr_runbooks"


def test_vector_upsert_and_count(client: TestClient):
    token = get_auth_token(client)
    
    upsert_res = client.post(
        "/api/v1/ai/vector/upsert",
        json={
            "collection_name": "enterprise_knowledge",
            "chunk_texts": [
                "New Q3 zero-trust perimeter policy with hardware key enforcement.",
                "Executive revenue targets established for Q4 2026.",
            ],
            "metadatas": [
                {"department": "SECURITY", "category": "POLICY_GOVERNANCE"},
                {"department": "FINANCE", "category": "FINANCIAL_FILING"},
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upsert_res.status_code == 200
    data = upsert_res.json()
    assert data["upserted_count"] == 2
    assert data["total_collection_vectors"] >= 2


def test_top_k_similarity_search(client: TestClient):
    token = get_auth_token(client)
    
    search_res = client.post(
        "/api/v1/ai/vector/search",
        json={
            "query": "What are the ISO 27001 access control guidelines?",
            "collection_name": "enterprise_knowledge",
            "top_k": 3,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search_res.status_code == 200
    data = search_res.json()
    assert data["total_matches"] > 0
    top_match = data["results"][0]
    assert top_match["score"] > 0.60
    assert "ISO" in top_match["document"] or "Security" in top_match["document"]


def test_metadata_filtering(client: TestClient):
    token = get_auth_token(client)
    
    # Filter only SECURITY
    search_res = client.post(
        "/api/v1/ai/vector/search",
        json={
            "query": "Enterprise performance guidelines",
            "collection_name": "enterprise_knowledge",
            "top_k": 5,
            "where_filter": {"department": "SECURITY"},
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search_res.status_code == 200
    data = search_res.json()
    assert data["total_matches"] > 0
    for r in data["results"]:
        assert r["metadata"]["department"] == "SECURITY"


def test_vector_store_stats(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/vector/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_vectors_indexed"] > 0
    assert data["active_collections_count"] >= 4
