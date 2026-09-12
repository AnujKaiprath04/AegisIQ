from datetime import datetime, timezone
from app.mlops_registry.types import ModelStage, RegisteredModel


class CanaryDeploymentManager:
    """Zero-Downtime Canary Traffic Splitting and Production Promotion."""

    @classmethod
    def set_canary(cls, model: RegisteredModel, canary_split_pct: float) -> RegisteredModel:
        model.canary_traffic_split_pct = canary_split_pct
        return model

    @classmethod
    def promote_to_production(cls, model: RegisteredModel, version_str: str) -> RegisteredModel:
        now_str = datetime.now(timezone.utc).isoformat()
        for v in model.all_versions:
            if v.version_str == version_str:
                v.stage = ModelStage.PRODUCTION
                v.deployed_at = now_str
            elif v.stage == ModelStage.PRODUCTION:
                v.stage = ModelStage.ARCHIVED

        model.active_version = version_str
        model.canary_traffic_split_pct = 0.0
        model.last_retrained_at = now_str
        return model
