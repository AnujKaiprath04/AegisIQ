import time
from typing import List, Optional
from app.assistant_service.types import (
    BusinessRecommendationCard,
    EffortLevel,
    PersonaType,
    TimeHorizon,
)


class BusinessRecommendationEngine:
    """Synthesizes prioritized enterprise action cards with financial impact, effort, and ownership."""

    @classmethod
    def generate_recommendations(
        cls,
        topic_or_query: str,
        persona_type: PersonaType = PersonaType.CEO,
    ) -> List[BusinessRecommendationCard]:
        q = topic_or_query.lower()

        # 1. Security / InfoSec Context
        if any(k in q for k in ["security", "iso", "access", "threat", "firewall", "quarantine", "breach"]):
            return [
                BusinessRecommendationCard(
                    id="REC-SEC-01",
                    title="Enforce Hardware FIDO2 Security Keys for Tier-1 Systems",
                    description="Mandate cryptographic hardware tokens for all cloud engineering roles to eliminate credential-based phishing vulnerabilities.",
                    expected_impact_usd=850000.0,
                    effort_level=EffortLevel.LOW,
                    time_horizon=TimeHorizon.THIRTY_DAYS,
                    department="SECURITY",
                    priority_rank=1,
                ),
                BusinessRecommendationCard(
                    id="REC-SEC-02",
                    title="Automate SIEM Edge Firewall IP Quarantine Playbooks",
                    description="Deploy automated threshold scripts to isolate malicious subnets exhibiting >20 failed login attempts within 60 seconds.",
                    expected_impact_usd=420000.0,
                    effort_level=EffortLevel.MEDIUM,
                    time_horizon=TimeHorizon.THIRTY_DAYS,
                    department="SECURITY",
                    priority_rank=2,
                ),
            ]

        # 2. Financial / Revenue / Sales Context
        if any(k in q for k in ["finance", "revenue", "arr", "margin", "ebitda", "sales", "cac", "churn", "growth"]):
            return [
                BusinessRecommendationCard(
                    id="REC-FIN-01",
                    title="Accelerate Enterprise Tier-1 Account Expansion",
                    description="Target high-utilization accounts with pre-approved seat expansion bundles to capitalize on current 114.2% Net Revenue Retention.",
                    expected_impact_usd=1250000.0,
                    effort_level=EffortLevel.LOW,
                    time_horizon=TimeHorizon.NINETY_DAYS,
                    department="SALES",
                    priority_rank=1,
                ),
                BusinessRecommendationCard(
                    id="REC-FIN-02",
                    title="Proactive Customer Success Intervention for Churn Accounts",
                    description="Trigger executive account reviews for Apex Global Logistics and Nexus FinTech to resolve overdue receivables and reverse seat drop.",
                    expected_impact_usd=480000.0,
                    effort_level=EffortLevel.MEDIUM,
                    time_horizon=TimeHorizon.THIRTY_DAYS,
                    department="FINANCE",
                    priority_rank=2,
                ),
                BusinessRecommendationCard(
                    id="REC-FIN-03",
                    title="Cloud Compute & Container Rightsizing Program",
                    description="Prune idle development cluster instances and enable autoscaling to reduce monthly AWS/GCP infrastructure expenditure by 14%.",
                    expected_impact_usd=240000.0,
                    effort_level=EffortLevel.LOW,
                    time_horizon=TimeHorizon.THIRTY_DAYS,
                    department="ENGINEERING",
                    priority_rank=3,
                ),
            ]

        # 3. Default General Executive Strategy
        return [
            BusinessRecommendationCard(
                id="REC-STRAT-01",
                title="Consolidate AI Decision Models into Central Gateway",
                description="Unify predictive churn and Holt-Winters forecasting into the automated executive briefing pipeline.",
                expected_impact_usd=620000.0,
                effort_level=EffortLevel.LOW,
                time_horizon=TimeHorizon.THIRTY_DAYS,
                department="EXECUTIVE",
                priority_rank=1,
            ),
            BusinessRecommendationCard(
                id="REC-STRAT-02",
                title="Automate Multi-Region Availability Zone Failover",
                description="Implement automated DNS routing failover across secondary regions to ensure 99.99% contractual SLA compliance.",
                expected_impact_usd=1500000.0,
                effort_level=EffortLevel.HIGH,
                time_horizon=TimeHorizon.NINETY_DAYS,
                department="ENGINEERING",
                priority_rank=2,
            ),
        ]
