import math
import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_embedding_model_registry_list(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/embedding/models",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["models"]) == 4
    model_types = [m["model_type"] for m in data["models"]]
    assert "BGE_SMALL" in model_types
    assert "MINILM_L6" in model_types
    assert "E5_SMALL" in model_types
    assert "LOCAL_ENTERPRISE" in model_types


def test_batch_embedding_generation_and_l2_norm(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/embedding/generate",
        json={"texts": ["ISO 27001 access control standard.", "Quarterly revenue pacing at $24.8M."]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_texts_embedded"] == 2
    assert data["dimensions"] == 384
    assert len(data["embeddings"]) == 2
    
    # Check L2 Euclidean normalization (norm ~= 1.0)
    for vec in data["embeddings"]:
        assert len(vec) == 384
        norm = math.sqrt(sum(x * x for x in vec))
        assert abs(norm - 1.0) < 0.01


def test_asymmetric_query_embedding(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/embedding/query",
        json={"query": "What are our high-risk customer churn accounts?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["dimensions"] == 384
    assert len(data["query_embedding"]) == 384
    norm = math.sqrt(sum(x * x for x in data["query_embedding"]))
    assert abs(norm - 1.0) < 0.01


def test_switch_active_embedding_model(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/embedding/switch-model",
        json={"model_type": "MINILM_L6"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "MINILM_L6" in data["message"] or "MiniLM" in data["active_model"]


def test_embedding_similarity_benchmark(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/embedding/benchmark",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["semantic_match_security"] > data["cross_domain_similarity_low"]
    assert data["semantic_match_finance"] > data["cross_domain_similarity_low"]
    assert data["benchmark_status"].startswith("PASSED")
