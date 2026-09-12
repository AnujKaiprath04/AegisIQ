# Import all the models, so that Base has them before being
# imported by Alembic or used for create_all.
from app.db.session import Base  # noqa
from app.models.user import User, Role, UserRole  # noqa
from app.models.audit import UserActivityLog  # noqa
from app.models.dataset import Dataset, ETLPipelineRun, DataQualityReport  # noqa
from app.models.kpi import KPIMetric, GeneratedReport  # noqa
from app.models.integration import DataConnection, MetadataCatalogTable, MetadataCatalogColumn, IngestionJob  # noqa
from app.models.assistant import AIConversation, AIMessage  # noqa
from app.models.knowledge import KnowledgeDocument, DocumentChunk, RAGSearchQuery  # noqa
from app.models.predictive import MLModelRegistry, ForecastPrediction, CustomerChurnPrediction  # noqa
from app.models.xai import XAIExplanationSession, XAIFeatureContribution, WhatIfSimulationLog  # noqa
from app.models.cybersecurity import SecurityIncident, IPBlocklistEntry, ZeroTrustScorecard  # noqa
from app.models.notification import NotificationItem, AlertRule, WebhookDeliveryLog  # noqa
from app.models.knowledge_base import KnowledgeBaseDocument  # noqa









