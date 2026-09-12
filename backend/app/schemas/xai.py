from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GlobalFeatureImportanceItem(BaseModel):
    feature_name: str
    mean_shap_value: float
    relative_importance_pct: float
    primary_impact: str  # POSITIVE_DRIVER, NEGATIVE_DRIVER
    description: str


class GlobalFeatureImportanceResponse(BaseModel):
    model_name: str
    model_type: str
    base_value: float
    features: List[GlobalFeatureImportanceItem] = []


class LocalFeatureContribution(BaseModel):
    feature_name: str
    feature_value: str
    shap_value: float  # e.g. +0.28, -0.12
    contribution_direction: str  # INCREASES_RISK, DECREASES_RISK
    importance_rank: int

    class Config:
        from_attributes = True


class WaterfallExplanationResponse(BaseModel):
    session_id: int
    entity_name: str
    model_type: str
    base_value: float
    predicted_value: float
    explanation_method: str
    contributions: List[LocalFeatureContribution] = []
    executive_summary: str


class WhatIfSimulationRequest(BaseModel):
    entity_id: Optional[int] = None
    weekly_active_seats_pct: float = Field(..., ge=0.0, le=100.0, description="Active seat usage percentage (0-100%)")
    invoice_overdue_days: int = Field(..., ge=0, le=180, description="Invoice payment delay in days")
    support_ticket_count: int = Field(..., ge=0, le=50, description="Open Level-1/2 support tickets")
    contract_length_months: int = Field(..., ge=1, le=60, description="Contract duration in months")


class WhatIfSimulationResponse(BaseModel):
    original_churn_probability_pct: float
    simulated_churn_probability_pct: float
    delta_pct: float
    risk_tier_change: str  # e.g. "HIGH_RISK -> LOW_RISK"
    simulated_contributions: List[LocalFeatureContribution] = []
    recommendation: str


class ModelFairnessMetricsResponse(BaseModel):
    disparate_impact_ratio: float
    equal_opportunity_difference: float
    demographic_parity_score: float
    fairness_verdict: str  # CERTIFIED_FAIR, LOW_BIAS, ACTION_REQUIRED
    cohort_parity_breakdown: Dict[str, float] = {}
    audit_timestamp: datetime
