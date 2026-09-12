# AegisIQ Enterprise Decision Intelligence Platform
## Platform Administrator & SRE Operational Runbook

**Document Version:** 1.0.0  
**Target Audience:** Site Reliability Engineers (SREs), Platform Admins, SOC Security Engineers  

---

## 1. Routine Operational Procedures

### 1.1 Database Backup & Snapshot Routine
- **Automated Backup Schedule**: Daily snapshot at 02:00 UTC with 30-day point-in-time retention.
- **Manual Hot Backup Command**:
  ```bash
  pg_dump -h ep-aegisiq-pooler.neon.tech -U aegis_admin -d aegisiq_production -Fc > backup_$(date +%Y%m%d_%H%M%S).dump
  ```
- **Database Restoration Command**:
  ```bash
  pg_restore -h ep-aegisiq-pooler.neon.tech -U aegis_admin -d aegisiq_production -c -v backup_target.dump
  ```

### 1.2 Redis Cache Namespace Invalidation
When deploying new ML models or updating enterprise knowledge base documents:
```bash
# Invalidate ML predictions cache
curl -X POST "https://api.aegisiq.com/api/v1/ops/performance/cache/flush" \
     -H "Authorization: Bearer $ADMIN_JWT" \
     -H "Content-Type: application/json" \
     -d '{"namespace": "ML_PREDICTIONS"}'
```

---

## 2. Incident Response Playbooks

### Playbook 1: Alert `HighHttpErrorRate` Spikes (> 5%)
1. **Initial Triage**: Open Grafana Error Rate Panel (`:3001`).
2. **Log Inspection**: Query Loki for recent 5xx exceptions:
   ```logql
   {job="aegisiq-backend"} |= "level=ERROR"
   ```
3. **Database Connection Pool Check**: Inspect active DB connections on `/api/v1/ops/observability/overview`.
4. **Emergency Rollback**: If caused by a faulty deployment, trigger the GitHub Actions rollback workflow:
   ```bash
   gh workflow run rollback.yml -f target_version=v1.3.0
   ```

### Playbook 2: Alert `ElevatedApiLatencyP99` (> 500ms)
1. **Identify Slow Queries**: Inspect PostgreSQL query profile endpoints on `/api/v1/ops/performance/overview`.
2. **Verify Index Integrity**: Run `ANALYZE audit_logs;` and `ANALYZE kpi_metrics;`.
3. **Scale Replicas**: If CPU exceeds 80%, increase Kubernetes replica count:
   ```bash
   kubectl scale deployment aegisiq-backend --replicas=5 -n aegisiq-prod
   ```

### Playbook 3: Alert `ModelPredictionDriftAnomaly` (PSI > 0.25)
1. **Review Drift Score**: Check `/api/v1/ml/registry/models` for active model PSI ratings.
2. **Trigger Automated Retraining**: Run the MLOps pipeline on updated ingestion datasets.
3. **Approve Canary Deployment**: Validate challenger model F1 score and promote to active champion.

---

## 3. Disaster Recovery & Emergency Contacts

| Incident Level | Response Time (SLA) | Primary Contact | Escalation Contact |
|---|---|---|---|
| **P1 - Critical Outage** | $\le 15$ mins | SRE Incident Commander (`sre@aegisiq.com`) | Head of Infrastructure |
| **P2 - Degraded Performance** | $\le 30$ mins | Platform Operations (`ops@aegisiq.com`) | Lead SRE |
| **P3 - Minor Anomaly** | $\le 4$ hours | Application Engineering | DevOps Team |
