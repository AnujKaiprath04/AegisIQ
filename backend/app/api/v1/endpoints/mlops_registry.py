from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.mlops_registry import (
    CanaryDeployRequest,
    DriftMetricSchema,
    FullIntelligenceSweepResponse,
    MasterIntelligenceStatusSchema,
    ModelDriftResponse,
    ModelListResponse,
    ModelPromoteRequest,
    RegisteredModelSchema,
    RetrainingJobSchema,
)
from app.mlops_registry.engine import EnterpriseMLOpsRegistry
from app.mlops_registry.bridge import MasterIntelligenceBridge

router = APIRouter(tags=["Part 3 - Module 10: Model Management & MLOps Registry"])


# --- Model Management & Governance ---

@router.get("/ml/models", response_model=ModelListResponse)
def list_registered_models(
    current_user: User = Depends(get_current_user),
):
    """List all registered enterprise machine learning models with active production stages and performance metrics."""
    models = EnterpriseMLOpsRegistry.list_models()
    return ModelListResponse(
        total_models=len(models),
        models=[RegisteredModelSchema(**m.model_dump()) for m in models],
    )


@router.post("/ml/models/{model_id}/retrain", response_model=RetrainingJobSchema)
def trigger_model_retraining(
    model_id: str,
    current_user: User = Depends(get_current_user),
):
    """Trigger automated model retraining pipeline and compute updated performance lift."""
    job = EnterpriseMLOpsRegistry.trigger_retraining(model_id, triggered_by=current_user.email)
    return RetrainingJobSchema(**job.model_dump())


@router.get("/ml/models/{model_id}/drift", response_model=ModelDriftResponse)
def get_model_drift_metrics(
    model_id: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieve statistical feature data drift (PSI) and concept drift (KS-test) metrics."""
    metrics = EnterpriseMLOpsRegistry.get_drift_metrics(model_id)
    return ModelDriftResponse(
        model_id=model_id,
        total_features=len(metrics),
        metrics=[DriftMetricSchema(**m.model_dump()) for m in metrics],
    )


@router.post("/ml/models/{model_id}/deploy-canary", response_model=RegisteredModelSchema)
def deploy_canary_traffic_split(
    model_id: str,
    req: CanaryDeployRequest,
    current_user: User = Depends(get_current_user),
):
    """Configure dynamic canary traffic splitting (e.g. 90/10) for candidate model versions."""
    model = EnterpriseMLOpsRegistry.deploy_canary(model_id, req.canary_split_pct)
    return RegisteredModelSchema(**model.model_dump())


@router.post("/ml/models/{model_id}/promote", response_model=RegisteredModelSchema)
def promote_model_version(
    model_id: str,
    req: ModelPromoteRequest,
    current_user: User = Depends(get_current_user),
):
    """Promote a candidate canary model version to active production with zero downtime."""
    model = EnterpriseMLOpsRegistry.promote_model(model_id, req.version_str)
    return RegisteredModelSchema(**model.model_dump())


# --- Master Unified Intelligence Bridge ---

@router.get("/ml/master-bridge/status", response_model=MasterIntelligenceStatusSchema)
def get_master_intelligence_status(
    current_user: User = Depends(get_current_user),
):
    """Retrieve comprehensive platform health check and live metrics across all 10 Part 3 modules."""
    status_summary = MasterIntelligenceBridge.get_system_status()
    return MasterIntelligenceStatusSchema(**status_summary.model_dump())


@router.post("/ml/master-bridge/full-sweep", response_model=FullIntelligenceSweepResponse)
def execute_master_intelligence_sweep(
    current_user: User = Depends(get_current_user),
):
    """Execute end-to-end multi-domain intelligence sweep unifying all 10 modules in Part 3."""
    results = MasterIntelligenceBridge.run_full_sweep()
    return FullIntelligenceSweepResponse(**results)
