import time
from datetime import datetime, timezone
from typing import List

from app.cicd_ops.types import (
    CIPipelineRun,
    DeploymentReleaseRecord,
    PipelineRunStatus,
    RollbackRequest,
    RollbackResult,
    WorkflowJobDetail,
)

PIPELINE_RUNS: List[CIPipelineRun] = [
    CIPipelineRun(
        run_id="run-gh-98412",
        commit_sha="a4f91b2c89",
        branch="main",
        author="lead-architect@aegisiq.com",
        status=PipelineRunStatus.SUCCESS,
        started_at="2026-08-31T10:00:00Z",
        completed_at="2026-08-31T10:04:12Z",
        jobs=[
            WorkflowJobDetail(job_name="backend-ci (Python 3.13)", status=PipelineRunStatus.SUCCESS, duration_seconds=114, summary="172 / 172 pytest tests passed. Ruff & Flake8: 0 linter violations."),
            WorkflowJobDetail(job_name="frontend-ci (Node 20)", status=PipelineRunStatus.SUCCESS, duration_seconds=88, summary="Next.js standalone production build compiled successfully."),
            WorkflowJobDetail(job_name="trivy-scan", status=PipelineRunStatus.SUCCESS, duration_seconds=34, summary="0 Critical / 0 High CVE vulnerabilities detected."),
            WorkflowJobDetail(job_name="cd-deploy-ghcr", status=PipelineRunStatus.SUCCESS, duration_seconds=76, summary="Multi-stage Docker images pushed to ghcr.io/aegisiq/backend:v1.0.0."),
        ],
    ),
    CIPipelineRun(
        run_id="run-gh-98390",
        commit_sha="c3b88d44e1",
        branch="staging",
        author="devops-engineer@aegisiq.com",
        status=PipelineRunStatus.SUCCESS,
        started_at="2026-08-31T08:30:00Z",
        completed_at="2026-08-31T08:33:45Z",
        jobs=[
            WorkflowJobDetail(job_name="backend-ci (Python 3.12)", status=PipelineRunStatus.SUCCESS, duration_seconds=105, summary="Pytest test matrix passed."),
            WorkflowJobDetail(job_name="frontend-ci (Node 18)", status=PipelineRunStatus.SUCCESS, duration_seconds=92, summary="Frontend build passed."),
        ],
    ),
]

RELEASES: List[DeploymentReleaseRecord] = [
    DeploymentReleaseRecord(
        release_tag="v1.0.0",
        commit_sha="a4f91b2c89",
        docker_digest="sha256:7f92b49c12a839f99401ab32cf09a1e0bca554",
        environment="production",
        deployed_at="2026-08-31T10:05:00Z",
        is_active=True,
    ),
    DeploymentReleaseRecord(
        release_tag="v0.9.8-rc2",
        commit_sha="e129fbb002",
        docker_digest="sha256:3a89012fce4589d98234ea7b654cd9182390ff",
        environment="production",
        deployed_at="2026-08-28T14:20:00Z",
        is_active=False,
    ),
]


class CICDDiagnosticsEngine:
    """CI/CD pipeline monitoring and automated rollback engine."""

    @classmethod
    def get_pipeline_runs(cls) -> List[CIPipelineRun]:
        return PIPELINE_RUNS

    @classmethod
    def get_releases(cls) -> List[DeploymentReleaseRecord]:
        return RELEASES

    @classmethod
    def trigger_rollback(cls, req: RollbackRequest) -> RollbackResult:
        now_str = datetime.now(timezone.utc).isoformat()
        current_active = next((r for r in RELEASES if r.is_active), RELEASES[0])
        previous_tag = current_active.release_tag

        # Update active pointers
        for r in RELEASES:
            r.is_active = (r.release_tag == req.target_tag)

        return RollbackResult(
            rollback_id=f"rollback-{int(time.time())}",
            status="ROLLBACK_EXECUTED_SUCCESSFULLY",
            previous_tag=previous_tag,
            restored_tag=req.target_tag,
            executed_at=now_str,
            health_check_passed=True,
        )
