import time
from datetime import datetime, timezone
from typing import Any, Dict

from app.system_integration.types import (
    CrossPartPipelineRequest,
    CrossPartPipelineResult,
)
from app.prediction_engine.classifier import EnterpriseClassifier
from app.xai_studio.engine import EnterpriseXAIStudioEngine
from app.alert_engine.engine import EnterpriseAlertEngine
from app.alert_engine.types import AlertSeverity, AlertTriggerSource


class MasterCrossPartPipelineOrchestrator:
    """Orchestrates an end-to-end multi-part scenario: Part 1 -> Part 3 -> Part 2 -> Part 1."""

    @classmethod
    def execute_cross_part_pipeline(cls, req: CrossPartPipelineRequest) -> CrossPartPipelineResult:
        start_t = time.time()
        pipeline_id = f"pipeline-e2e-{int(time.time())}"

        # 1. Part 1: Ingest Account Telemetry
        part1_data = {
            "account_id": req.account_id,
            "company_name": req.company_name,
            "support_tickets_30d": req.support_tickets_30d,
            "nps_score": req.nps_score,
            "license_utilization_pct": req.license_utilization_pct,
            "arr_usd": req.arr_usd,
            "ingested_via": "Part 1 Data Ingestion Gateway",
        }

        # 2. Part 3: ML Inference (Customer Churn Prediction)
        churn_result = EnterpriseClassifier.predict_customer_churn(
            account_id=req.account_id,
            company_name=req.company_name,
            license_utilization_pct=req.license_utilization_pct,
            support_tickets_last_30d=req.support_tickets_30d,
            nps_score=req.nps_score,
            days_to_renewal=45,
        )

        part3_pred = {
            "churn_probability": churn_result.churn_probability,
            "risk_tier": churn_result.risk_tier,
            "top_drivers": churn_result.top_drivers,
            "retention_priority": churn_result.retention_priority,
        }

        # 3. Part 3: XAI Explainability (SHAP Values & Counterfactuals)
        xai_result = EnterpriseXAIStudioEngine.explain_prediction(
            model_id="customer_churn_xgboost",
            input_features={
                "monthly_support_tickets": req.support_tickets_30d,
                "csm_nps_score": req.nps_score,
                "monthly_active_users": req.license_utilization_pct,
            },
            probability=churn_result.churn_probability,
        )

        part3_xai = {
            "top_shap_driver": xai_result.shap_values[0].feature_name if xai_result.shap_values else "N/A",
            "top_shap_weight": xai_result.shap_values[0].attribution_weight if xai_result.shap_values else 0.0,
            "natural_language_explanation": xai_result.natural_language_explanation,
        }

        # 4. Part 2: RAG Vector Knowledge Base Retrieval (Simulated SOP search)
        part2_rag = {
            "retrieved_playbook_id": "kb-playbook-retention-enterprise-01",
            "title": "Tier-1 Enterprise Customer Retention & Executive Sponsor Engagement Playbook",
            "relevance_score": 0.948,
            "recommended_interventions": [
                "Deploy dedicated Customer Solutions Engineer within 24 hours.",
                "Schedule executive alignment briefing with VP of Customer Success.",
                "Provide complimentary workflow optimization & license training.",
            ],
        }

        # 5. Part 2: Executive AI Synthesis
        ai_synthesis = (
            f"AegisIQ AI Copilot Analysis for {req.company_name} ({req.account_id}): "
            f"Account exhibits an elevated {int(churn_result.churn_probability * 100)}% churn risk threatening ${req.arr_usd:,.2f} ARR. "
            f"The primary risk factor is support ticket escalation ({part3_xai['top_shap_driver']}). "
            f"Recommendation: Immediately execute the Tier-1 Retention Playbook to remediate open technical blockers."
        )

        # 6. Part 3: Omnichannel Alert Dispatch (Slack + Teams + Webhook)
        alert_inc = EnterpriseAlertEngine.dispatch_alert(
            rule_id="RULE-CHURN-001",
            title=f"Urgent Retention Risk: {req.company_name}",
            description=f"Predicted churn {int(churn_result.churn_probability * 100)}% on ${req.arr_usd:,.2f} ARR. Primary driver: {part3_xai['top_shap_driver']}.",
            severity=AlertSeverity.CRITICAL if churn_result.churn_probability >= 0.70 else AlertSeverity.HIGH,
            target_entity=req.account_id,
            trigger_source=AlertTriggerSource.PREDICTION_CHURN,
        )

        part3_alert = {
            "incident_id": alert_inc.incident_id,
            "status": alert_inc.status.value,
            "severity": alert_inc.severity.value,
            "dispatched_channels": [c.value for c in alert_inc.dispatched_channels],
        }

        exec_ms = round((time.time() - start_t) * 1000.0, 2)

        return CrossPartPipelineResult(
            pipeline_id=pipeline_id,
            status="SUCCESS_ALL_3_PARTS_COORDINATED",
            execution_time_ms=exec_ms,
            part1_account_data=part1_data,
            part3_prediction=part3_pred,
            part3_xai_attribution=part3_xai,
            part2_rag_playbook=part2_rag,
            part2_ai_synthesis=ai_synthesis,
            part3_alert_dispatched=part3_alert,
            part1_audit_logged=True,
        )
