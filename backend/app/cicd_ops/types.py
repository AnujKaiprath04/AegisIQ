from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PipelineRunStatus(str, Enum):
    SUCCESS = "SUCCESS"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class WorkflowJobDetail(BaseModel):
    job_name: str
    status: PipelineRunStatus
    duration_seconds: int
    summary: str


class CIPipelineRun(BaseModel):
    run_id: str
    commit_sha: str
    branch: str
    author: str
    status: PipelineRunStatus
    started_at: str
    completed_at: Optional[str] = None
    jobs: List[WorkflowJobDetail] = []


class DeploymentReleaseRecord(BaseModel):
    release_tag: str
    commit_sha: str
    docker_digest: str
    environment: str = "production"
    deployed_at: str
    is_active: bool


class RollbackRequest(BaseModel):
    target_tag: str = Field(default="v1.0.0", description="Target release tag to roll back to")
    reason: str = Field(default="Automated healthcheck regression detected", description="Reason for rollback")


class RollbackResult(BaseModel):
    rollback_id: str
    status: str
    previous_tag: str
    restored_tag: str
    executed_at: str
    health_check_passed: bool = True
