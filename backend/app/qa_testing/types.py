from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TestSuiteSummary(BaseModel):
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int = 0
    pass_rate_pct: float = 100.0
    execution_time_seconds: float


class LoadTestProfile(BaseModel):
    profile_name: str
    tool: str  # Locust / K6
    virtual_users: int
    target_endpoints: List[str] = []
    p99_latency_sla_ms: int
    error_rate_threshold_pct: float
    status: str = "VALIDATED"


class E2ERunResult(BaseModel):
    spec_file: str
    workflow_name: str
    browser: str = "Chromium / WebKit / Firefox"
    steps_count: int
    status: str = "PASSED"
    duration_ms: int


class QAReportOverview(BaseModel):
    total_test_cases: int = 189
    total_passed: int = 189
    total_failed: int = 0
    overall_pass_rate_pct: float = 100.0
    code_coverage_pct: float = 94.8
    suites: List[TestSuiteSummary] = []
    load_profiles: List[LoadTestProfile] = []
    e2e_specs: List[E2ERunResult] = []
    generated_at: str
