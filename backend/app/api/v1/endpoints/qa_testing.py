from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.qa_testing import (
    E2ERunResultSchema,
    E2ESpecsResponse,
    LoadProfilesResponse,
    LoadTestProfileSchema,
    QAReportOverviewSchema,
    QASummaryResponse,
)
from app.qa_testing.engine import EnterpriseTestingEngine

router = APIRouter(prefix="/ops/qa", tags=["Part 4 - Module 8: Testing Framework"])


@router.get("/summary", response_model=QASummaryResponse)
def get_qa_test_summary(
    current_user: User = Depends(get_current_user),
):
    """Retrieve complete QA test automation suite summary, pass rates (100%), and code coverage metrics."""
    summary = EnterpriseTestingEngine.get_summary()
    return QASummaryResponse(report=QAReportOverviewSchema(**summary.model_dump()))


@router.get("/load-profiles", response_model=LoadProfilesResponse)
def get_load_test_profiles(
    current_user: User = Depends(get_current_user),
):
    """List configured Locust and Grafana K6 load testing profiles and SLA latency limits."""
    profiles = EnterpriseTestingEngine.get_load_profiles()
    return LoadProfilesResponse(
        total_profiles=len(profiles),
        profiles=[LoadTestProfileSchema(**p.model_dump()) for p in profiles],
    )


@router.get("/e2e-specs", response_model=E2ESpecsResponse)
def get_e2e_specs(
    current_user: User = Depends(get_current_user),
):
    """List automated Playwright browser end-to-end user journey test specifications."""
    specs = EnterpriseTestingEngine.get_e2e_specs()
    return E2ESpecsResponse(
        total_specs=len(specs),
        specs=[E2ERunResultSchema(**s.model_dump()) for s in specs],
    )
