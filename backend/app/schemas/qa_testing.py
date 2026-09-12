from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.qa_testing.types import (
    E2ERunResult,
    LoadTestProfile,
    QAReportOverview,
    TestSuiteSummary,
)


class TestSuiteSummarySchema(TestSuiteSummary):
    pass


class LoadTestProfileSchema(LoadTestProfile):
    pass


class E2ERunResultSchema(E2ERunResult):
    pass


class QAReportOverviewSchema(QAReportOverview):
    pass


class QASummaryResponse(BaseModel):
    report: QAReportOverviewSchema


class LoadProfilesResponse(BaseModel):
    total_profiles: int
    profiles: List[LoadTestProfileSchema] = []


class E2ESpecsResponse(BaseModel):
    total_specs: int
    specs: List[E2ERunResultSchema] = []
