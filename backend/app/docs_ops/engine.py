from datetime import datetime, timezone
from typing import List

from app.docs_ops.types import (
    ArchitectureLayerInfo,
    DocSectionMetadata,
    DocumentationOverview,
    IncidentPlaybook,
)

DOCS_CATALOG: List[DocSectionMetadata] = [
    DocSectionMetadata(
        doc_id="DOC-01",
        title="Software Requirements Specification (SRS)",
        filename="docs/SRS.md",
        description="Comprehensive functional, non-functional, security, and RBAC requirements.",
        total_sections=12,
    ),
    DocSectionMetadata(
        doc_id="DOC-02",
        title="High-Level Design (HLD)",
        filename="docs/HLD.md",
        description="System architectural topology, multi-tier layout, and end-to-end dataflow sequence diagrams.",
        total_sections=8,
    ),
    DocSectionMetadata(
        doc_id="DOC-03",
        title="Low-Level Design (LLD)",
        filename="docs/LLD.md",
        description="Database ERDs, token bucket rate limiter, input sanitizer, and TreeSHAP algorithmic formulas.",
        total_sections=10,
    ),
    DocSectionMetadata(
        doc_id="DOC-04",
        title="Production Deployment Guide",
        filename="docs/DEPLOYMENT_GUIDE.md",
        description="Step-by-step guides for Docker Compose, Kubernetes, Neon PostgreSQL, Vercel, and Render.",
        total_sections=7,
    ),
    DocSectionMetadata(
        doc_id="DOC-05",
        title="Platform Administrator Runbook",
        filename="docs/ADMIN_RUNBOOK.md",
        description="SRE incident response playbooks, automated backup/restore routines, and disaster recovery procedures.",
        total_sections=6,
    ),
]

ARCH_LAYERS: List[ArchitectureLayerInfo] = [
    ArchitectureLayerInfo(
        layer_name="1. Client & Edge Ingress Tier",
        technology_stack="Next.js 14, React 18, Tailwind CSS, Vercel Global Edge CDN, Nginx",
        responsibilities=["Static asset caching", "SSR rendering", "Reverse proxying", "TLS termination"],
    ),
    ArchitectureLayerInfo(
        layer_name="2. Security Gatekeeper & Hardening",
        technology_stack="OWASP Headers, Sliding-Window Token Bucket, Regex Threat Interceptor, JWT RS256",
        responsibilities=["HSTS/CSP enforcement", "Rate limit quota control", "SQLi/XSS neutralization", "5-Tier RBAC"],
    ),
    ArchitectureLayerInfo(
        layer_name="3. Core Application Kernel",
        technology_stack="Python 3.13, FastAPI ASGI, Pydantic v2, SQLAlchemy 2.0",
        responsibilities=["BI variance calculation", "RAG vector retrieval", "ML inference execution", "Immutable audit logging"],
    ),
    ArchitectureLayerInfo(
        layer_name="4. Persistence & Caching Tier",
        technology_stack="Neon PostgreSQL 16, PgBouncer, Redis 7.2, Supabase S3 Blob Storage",
        responsibilities=["ACID transactions", "L1 in-memory & L2 distributed cache", "Dataset/model storage"],
    ),
    ArchitectureLayerInfo(
        layer_name="5. Observability & SRE APM Stack",
        technology_stack="Prometheus, Grafana, Loki, Promtail, Alertmanager",
        responsibilities=["Telemetry metric scraping", "Structured log aggregation", "Automated alert paging"],
    ),
]

PLAYBOOKS: List[IncidentPlaybook] = [
    IncidentPlaybook(
        playbook_id="PB-01",
        alert_name="HighHttpErrorRate",
        severity="CRITICAL",
        trigger_condition="5xx error rate > 5% over 5m",
        mitigation_steps=["Check Loki logs for traceback exceptions", "Inspect DB connection pool saturation", "Trigger automated CD rollback if deployment-related"],
    ),
    IncidentPlaybook(
        playbook_id="PB-02",
        alert_name="ElevatedApiLatencyP99",
        severity="WARNING",
        trigger_condition="P99 response time > 500ms over 3m",
        mitigation_steps=["Inspect PostgreSQL query execution profiles", "Run database table vacuum analyze", "Scale Kubernetes backend pod replicas"],
    ),
    IncidentPlaybook(
        playbook_id="PB-03",
        alert_name="ModelPredictionDriftAnomaly",
        severity="WARNING",
        trigger_condition="Model PSI score > 0.25",
        mitigation_steps=["Inspect MLOps feature drift distributions", "Trigger automated canary model retraining", "Validate champion/challenger accuracy metrics"],
    ),
]


class EnterpriseDocumentationEngine:
    """Master Documentation and Architecture Blueprint Engine."""

    @classmethod
    def get_overview(cls) -> DocumentationOverview:
        now_str = datetime.now(timezone.utc).isoformat()
        return DocumentationOverview(
            total_documents=len(DOCS_CATALOG),
            total_architectural_layers=len(ARCH_LAYERS),
            total_incident_playbooks=len(PLAYBOOKS),
            documents=DOCS_CATALOG,
            timestamp=now_str,
        )

    @classmethod
    def get_architecture(cls) -> List[ArchitectureLayerInfo]:
        return ARCH_LAYERS

    @classmethod
    def get_playbooks(cls) -> List[IncidentPlaybook]:
        return PLAYBOOKS
