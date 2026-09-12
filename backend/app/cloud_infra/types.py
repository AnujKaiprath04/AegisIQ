from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CloudProvider(str, Enum):
    VERCEL = "VERCEL"
    RENDER = "RENDER"
    NEON_POSTGRES = "NEON_POSTGRES"
    SUPABASE_STORAGE = "SUPABASE_STORAGE"
    KUBERNETES = "KUBERNETES"


class CloudServiceStatus(str, Enum):
    ACTIVE_ONLINE = "ACTIVE_ONLINE"
    PROVISIONING = "PROVISIONING"
    MAINTENANCE = "MAINTENANCE"


class StorageBucketConfig(BaseModel):
    bucket_id: str
    name: str
    is_public: bool
    max_size_mb: int
    allowed_mime_types: List[str] = []
    rls_enabled: bool = True


class DatabaseTopologyInfo(BaseModel):
    provider: CloudProvider = CloudProvider.NEON_POSTGRES
    engine: str = "PostgreSQL 16.2 Serverless"
    ssl_enforced: bool = True
    pooling_driver: str = "PgBouncer Serverless Pooler (Port 6543)"
    auto_suspend_minutes: int = 5
    allocated_compute: str = "0.25 to 4.0 Compute Units (Dynamic Autoscaling)"
    status: CloudServiceStatus = CloudServiceStatus.ACTIVE_ONLINE


class CloudInfrastructureTopology(BaseModel):
    environment: str = "production"
    frontend_provider: str = "Vercel Serverless Edge Platform"
    frontend_status: CloudServiceStatus = CloudServiceStatus.ACTIVE_ONLINE
    backend_provider: str = "Render Managed Web Services"
    backend_status: CloudServiceStatus = CloudServiceStatus.ACTIVE_ONLINE
    database_info: DatabaseTopologyInfo
    storage_buckets: List[StorageBucketConfig] = []
    k8s_ready: bool = True
    last_health_check: str
