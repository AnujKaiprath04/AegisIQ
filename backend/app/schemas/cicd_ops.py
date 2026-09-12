from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.cicd_ops.types import (
    CIPipelineRun,
    DeploymentReleaseRecord,
    RollbackRequest,
    RollbackResult,
    WorkflowJobDetail,
)


class WorkflowJobDetailSchema(WorkflowJobDetail):
    pass


class CIPipelineRunSchema(CIPipelineRun):
    pass


class DeploymentReleaseRecordSchema(DeploymentReleaseRecord):
    pass


class RollbackRequestSchema(RollbackRequest):
    pass


class RollbackResultSchema(RollbackResult):
    pass


class CIPipelineRunsResponse(BaseModel):
    total_runs: int
    runs: List[CIPipelineRunSchema] = []


class DeploymentReleasesResponse(BaseModel):
    total_releases: int
    releases: List[DeploymentReleaseRecordSchema] = []


class RollbackResponse(BaseModel):
    result: RollbackResultSchema
