from fastapi import APIRouter
from app.api.v1.endpoints import auth, system, users, datasets, etl, bi, kpis, reports, audit, integration, assistant, knowledge, predictive, xai, cybersecurity, notifications, telemetry, ai_gateway, knowledge_base, document_pipeline, embedding, vector_store, rag_engine, enterprise_assistant, prompt_engine, conversation_memory, explainability, report_generator, business_api, enterprise_analytics, data_prep, predictive_engine, recommendation_engine, risk_engine, security_engine, anomaly_engine, xai_studio, alert_engine, mlops_registry, system_integration, container_ops, cloud_infra, cicd_ops, security_hardening, monitoring_logging, performance_ops, qa_testing, docs_ops, delivery_ops

api_router = APIRouter()

api_router.include_router(system.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(integration.router)
api_router.include_router(datasets.router)
api_router.include_router(etl.router)
api_router.include_router(bi.router)
api_router.include_router(kpis.router)
api_router.include_router(assistant.router)
api_router.include_router(knowledge.router)
api_router.include_router(predictive.router)
api_router.include_router(xai.router)
api_router.include_router(cybersecurity.router)
api_router.include_router(notifications.router)
api_router.include_router(telemetry.router)
api_router.include_router(ai_gateway.router)
api_router.include_router(knowledge_base.router)
api_router.include_router(document_pipeline.router)
api_router.include_router(embedding.router)
api_router.include_router(vector_store.router)
api_router.include_router(rag_engine.router)
api_router.include_router(enterprise_assistant.router)
api_router.include_router(prompt_engine.router)
api_router.include_router(conversation_memory.router)
api_router.include_router(explainability.router)
api_router.include_router(report_generator.router)
api_router.include_router(business_api.router)
api_router.include_router(enterprise_analytics.router)
api_router.include_router(data_prep.router)
api_router.include_router(predictive_engine.router)
api_router.include_router(recommendation_engine.router)
api_router.include_router(risk_engine.router)
api_router.include_router(security_engine.router)
api_router.include_router(anomaly_engine.router)
api_router.include_router(xai_studio.router)
api_router.include_router(alert_engine.router)
api_router.include_router(mlops_registry.router)
api_router.include_router(system_integration.router)
api_router.include_router(container_ops.router)
api_router.include_router(cloud_infra.router)
api_router.include_router(cicd_ops.router)
api_router.include_router(security_hardening.router)
api_router.include_router(monitoring_logging.router)
api_router.include_router(performance_ops.router)
api_router.include_router(qa_testing.router)
api_router.include_router(docs_ops.router)
api_router.include_router(delivery_ops.router)
api_router.include_router(reports.router)
api_router.include_router(audit.router)









































