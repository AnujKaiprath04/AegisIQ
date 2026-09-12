from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.performance_ops.cache import MultiTierCacheManager
from app.performance_ops.types import CacheNamespace


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_performance_overview_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/performance/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    ov = data["overview"]
    assert ov["overall_cache_hit_rate_pct"] >= 90.0
    assert ov["p99_latency_ms"] < 50.0
    assert ov["compression_ratio_pct"] >= 70.0
    assert len(ov["cache_tiers"]) >= 2
    assert len(ov["query_profiles"]) >= 4


def test_cache_tier_stats_and_flush(client: TestClient):
    token = get_auth_token(client)

    # 1. Get Cache Stats
    res = client.get(
        "/api/v1/ops/performance/cache",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_tiers"] >= 2
    tier_names = [t["tier_name"] for t in data["tiers"]]
    assert any("L1" in name for name in tier_names)
    assert any("L2" in name for name in tier_names)

    # 2. Flush Cache Namespace
    flush_res = client.post(
        "/api/v1/ops/performance/cache/flush",
        json={"namespace": "BI_DASHBOARD"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert flush_res.status_code == 200
    flush_data = flush_res.json()["result"]
    assert flush_data["status"] == "CACHE_NAMESPACE_INVALIDATED_SUCCESSFULLY"
    assert flush_data["namespace"] == "BI_DASHBOARD"
    assert flush_data["flushed_keys_count"] >= 0


def test_multitier_cache_manager_logic():
    MultiTierCacheManager.set("test:key:revenue", {"q3_revenue": 4500000}, ttl_seconds=60)
    cached_val = MultiTierCacheManager.get("test:key:revenue")
    assert cached_val is not None
    assert cached_val["q3_revenue"] == 4500000

    # Test non-existent key
    miss_val = MultiTierCacheManager.get("test:key:non_existent")
    assert miss_val is None


def test_performance_sql_and_next_config_exist():
    # Base repo path: c:/Work to do/FYP
    repo_root = Path(__file__).resolve().parent.parent.parent

    sql_indexes = repo_root / "deployment" / "performance_indexes.sql"
    next_config = repo_root / "frontend" / "next.config.ts"

    assert sql_indexes.exists()
    assert next_config.exists()

    # Content assertions
    sql_content = sql_indexes.read_text(encoding="utf-8")
    assert "idx_audit_logs_timestamp_user" in sql_content
    assert "idx_telemetry_timestamp_brin" in sql_content
    assert "BRIN" in sql_content

    next_content = next_config.read_text(encoding="utf-8")
    assert "compress: true" in next_content
    assert "standalone" in next_content
