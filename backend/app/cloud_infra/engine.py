from datetime import datetime, timezone
from typing import List

from app.cloud_infra.types import (
    CloudInfrastructureTopology,
    CloudServiceStatus,
    DatabaseTopologyInfo,
    StorageBucketConfig,
)

STORAGE_BUCKETS: List[StorageBucketConfig] = [
    StorageBucketConfig(
        bucket_id="aegisiq-datasets",
        name="Enterprise Raw & Ingested Datasets",
        is_public=False,
        max_size_mb=100,
        allowed_mime_types=["text/csv", "application/json", "application/parquet"],
        rls_enabled=True,
    ),
    StorageBucketConfig(
        bucket_id="aegisiq-ml-artifacts",
        name="Serialized Machine Learning Model Weights",
        is_public=False,
        max_size_mb=500,
        allowed_mime_types=["application/octet-stream", "application/x-pickle", "application/json"],
        rls_enabled=True,
    ),
    StorageBucketConfig(
        bucket_id="aegisiq-reports",
        name="Executive Compliance & BI PDF Reports",
        is_public=False,
        max_size_mb=50,
        allowed_mime_types=["application/pdf", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
        rls_enabled=True,
    ),
    StorageBucketConfig(
        bucket_id="aegisiq-backups",
        name="Encrypted Automated Database Backups",
        is_public=False,
        max_size_mb=1024,
        allowed_mime_types=["application/gzip", "application/zip", "application/octet-stream"],
        rls_enabled=True,
    ),
]


class CloudInfrastructureManager:
    """Production Cloud Infrastructure Manager (Vercel, Render, Neon, Supabase, K8s)."""

    @classmethod
    def get_topology(cls) -> CloudInfrastructureTopology:
        now_str = datetime.now(timezone.utc).isoformat()
        return CloudInfrastructureTopology(
            environment="production",
            frontend_provider="Vercel Serverless Edge Platform (Global Anycast)",
            frontend_status=CloudServiceStatus.ACTIVE_ONLINE,
            backend_provider="Render Managed Web Services (Oregon Region)",
            backend_status=CloudServiceStatus.ACTIVE_ONLINE,
            database_info=cls.get_database_info(),
            storage_buckets=STORAGE_BUCKETS,
            k8s_ready=True,
            last_health_check=now_str,
        )

    @classmethod
    def get_storage_buckets(cls) -> List[StorageBucketConfig]:
        return STORAGE_BUCKETS

    @classmethod
    def get_database_info(cls) -> DatabaseTopologyInfo:
        return DatabaseTopologyInfo()
