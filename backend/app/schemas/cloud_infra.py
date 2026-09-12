from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.cloud_infra.types import (
    CloudInfrastructureTopology,
    DatabaseTopologyInfo,
    StorageBucketConfig,
)


class StorageBucketConfigSchema(StorageBucketConfig):
    pass


class DatabaseTopologyInfoSchema(DatabaseTopologyInfo):
    pass


class CloudInfrastructureTopologySchema(CloudInfrastructureTopology):
    pass


class CloudTopologyResponse(BaseModel):
    topology: CloudInfrastructureTopologySchema


class CloudStorageResponse(BaseModel):
    total_buckets: int
    buckets: List[StorageBucketConfigSchema] = []


class CloudDatabaseResponse(BaseModel):
    database: DatabaseTopologyInfoSchema
