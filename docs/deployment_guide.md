# AegisIQ Enterprise Decision Intelligence Platform
## Production Deployment Guide

**Document Version:** 1.0.0  
**Target Environments:** Local Docker Compose, Kubernetes (EKS/GKE/AKS), Neon PostgreSQL, Vercel & Render  

---

## 1. Prerequisites & Tooling

Before deploying AegisIQ, ensure the following command-line tools are installed:
- **Docker Engine** 24.0+ & **Docker Compose** v2.20+
- **Kubernetes CLI (`kubectl`)** v1.28+
- **Node.js** 20.x+ & **npm** 10.x+
- **Python** 3.12+ / 3.13+ & **pip**

---

## 2. Option A: Local Multi-Container Deployment (Docker Compose)

### 2.1 Clone Repository & Prepare Environment Variables
```bash
git clone https://github.com/aegisiq-org/aegisiq.git
cd aegisiq
cp .env.example .env
```

### 2.2 Launch Multi-Service Production Stack
```bash
# Build and start all 8 services in background
docker compose -f docker-compose.prod.yml up -d --build
```

### 2.3 Verify Service Accessibility
- **Frontend Dashboard**: `http://localhost:3000`
- **FastAPI Core API Docs**: `http://localhost:8000/docs`
- **Prometheus Telemetry**: `http://localhost:9090`
- **Grafana Dashboards**: `http://localhost:3001` (Default: `admin` / `admin`)
- **Loki Log Ingestion**: `http://localhost:3100`

---

## 3. Option B: Kubernetes Production Cluster Deployment

### 3.1 Create Namespace & Secrets
```bash
kubectl apply -f deployment/k8s/namespace.yaml
kubectl apply -f deployment/k8s/secrets.yaml
kubectl apply -f deployment/k8s/configmap.yaml
```

### 3.2 Deploy Backend, Frontend & Autoscaler
```bash
kubectl apply -f deployment/k8s/backend-deployment.yaml
kubectl apply -f deployment/k8s/frontend-deployment.yaml
kubectl apply -f deployment/k8s/ingress.yaml
```

### 3.3 Verify Cluster Health & Pod Autoscaling
```bash
kubectl get pods -n aegisiq-prod
kubectl get hpa -n aegisiq-prod
kubectl get ingress -n aegisiq-prod
```

---

## 4. Option C: Cloud Hybrid Deployment (Vercel + Render + Neon)

### 4.1 Neon Serverless PostgreSQL Setup
1. Create database in Neon Console (`aegisiq_production`).
2. Run database initialization script:
   ```bash
   psql -h ep-aegisiq-pooler.neon.tech -U aegis_admin -d aegisiq_production -f deployment/neon_db_setup.sql
   psql -h ep-aegisiq-pooler.neon.tech -U aegis_admin -d aegisiq_production -f deployment/performance_indexes.sql
   ```

### 4.2 Backend API Deployment on Render
1. Connect GitHub repository to Render.
2. Select Blueprint deployment using `render.yaml`.
3. Set environment variable `DATABASE_URL` pointing to the Neon PgBouncer pooled connection URI.

### 4.3 Frontend Edge Deployment on Vercel
1. Import `frontend/` directory in Vercel.
2. Ensure `vercel.json` rewrite proxy points `/api/*` to the Render backend domain.
3. Deploy to production edge.
