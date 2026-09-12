# AegisIQ Enterprise Decision Intelligence Platform
## High-Level Design (HLD) Document

**Document Version:** 1.0.0  
**Status:** Approved & Verified  
**Classification:** Enterprise Confidential  

---

## 1. System Overview & Architectural Topology

AegisIQ is engineered using a modular, decoupled micro-layered architecture designed for high availability, sub-50ms query latency, and zero-trust perimeter security.

```mermaid
graph TD
    subgraph ClientEdge ["Client & Edge Ingress Tier"]
        USER[Enterprise Client Browser]
        CDN[Vercel Global Edge CDN / Next.js UI :3000]
        NGINX[Nginx Hardened Reverse Proxy :80/:443]
    end

    subgraph SecurityShield ["Perimeter Defense & Security Layer"]
        HSTS[OWASP Security Headers & CSP]
        RATELIMIT[Sliding-Window Token Bucket Limiter]
        SANITIZER[Deep Input Threat Sanitizer]
        AUTH_RBAC[JWT RS256 & 5-Tier RBAC]
    end

    subgraph ApplicationKernel ["AegisIQ Core Application Kernel (FastAPI :8000)"]
        BI_ENGINE[Part 1: BI Variance & ETL Pipeline]
        RAG_ENGINE[Part 2: Hybrid RAG & Vector Copilot]
        ML_ENGINE[Part 3: 7 Predictive Models & XAI Studio]
        ORCHESTRATOR[Part 4: System Integration Master Pipeline]
    end

    subgraph PerformanceAndCache ["Multi-Tier Caching & Persistence"]
        L1_MEM[L1 In-Memory LRU Cache]
        L2_REDIS[L2 Redis Cluster :6379]
        POSTGRES[(Neon PostgreSQL 16 DB with PgBouncer :6543)]
        S3_STORAGE[Supabase S3 Blob Storage]
    end

    subgraph ObservabilityAPM ["Observability & APM Stack"]
        PROM[Prometheus :9090]
        LOKI[Grafana Loki :3100]
        GRAFANA[Grafana Dashboards :3001]
        ALERTMANAGER[Alertmanager :9093]
    end

    USER --> CDN --> NGINX --> HSTS --> RATELIMIT --> SANITIZER --> AUTH_RBAC --> ApplicationKernel
    ApplicationKernel --> L1_MEM
    L1_MEM -->|Miss| L2_REDIS -->|Miss| POSTGRES
    ApplicationKernel --> S3_STORAGE
    ApplicationKernel -->|Metrics /metrics| PROM --> GRAFANA
    ApplicationKernel -->|JSON Logs| LOKI --> GRAFANA
    PROM --> ALERTMANAGER
```

---

## 2. Multi-Tier Layer Architecture

### 2.1 Tier 1: Client & Edge Tier (Vercel & Next.js)
- **Framework**: Next.js 14 App Router, React 18, TypeScript, Tailwind CSS.
- **Delivery**: Global edge CDN caching with automated minification and code splitting.
- **Rendering**: Server-Side Rendering (SSR) for initial loads and dynamic client-side hydration for real-time WebSocket and telemetry updates.

### 2.2 Tier 2: Hardened Ingress & Security Gatekeeper (Nginx & Middleware)
- **Nginx Reverse Proxy**: SSL/TLS termination with modern ciphers (TLSv1.3), Gzip compression, and rate limiting.
- **ASGI Security Middleware**:
  - `SecurityHeadersMiddleware`: Enforces HSTS, CSP, X-Frame-Options, and nosniff.
  - `EnterpriseTokenBucketRateLimiter`: Multi-tier quota enforcement.
  - `EnterpriseInputSanitizer`: Intercepts and cleans SQLi, XSS, and command injection attacks.

### 2.3 Tier 3: Core Application Micro-Modules (FastAPI)
- **Part 1 Core Platform**: ETL data pipelines, variance calculus, BI data structures, and immutable audit logs.
- **Part 2 Generative AI**: Document parser, text chunker, dense vector embeddings, and LLM orchestration.
- **Part 3 Machine Learning & XAI**: Scikit-Learn / XGBoost models, TreeSHAP / LIME explainers, and SIEM threat scanner.
- **Part 4 System Integration**: Cross-part master scenarios and operational health diagnostics.

### 2.4 Tier 4: Multi-Tier Data Persistence & Cache
- **L1 In-Memory Cache**: High-speed memory store with TTL ($< 0.5\text{ms}$).
- **L2 Redis Cache**: Distributed cache with namespace invalidation (`CACHE:BI:*`, `CACHE:ML:*`, `CACHE:RAG:*`).
- **PostgreSQL 16 Database**: Relational transactional database configured with PgBouncer connection pooling and composite B-Tree/BRIN indexes.

---

## 3. End-to-End Master Dataflow

```mermaid
sequenceDiagram
    autonumber
    actor User as Enterprise Analyst
    participant Edge as Next.js UI / Nginx
    participant Sec as Security Gatekeeper
    participant API as FastAPI Backend
    participant ML as ML Inference Engine
    participant XAI as TreeSHAP / LIME Studio
    participant RAG as Hybrid RAG Copilot
    participant DB as PostgreSQL DB

    User->>Edge: Submit Customer Retention Analysis Request
    Edge->>Sec: Forward Request with JWT Token
    Sec->>Sec: Validate Token, Rate Limit & Threat Sanitize
    Sec->>API: Route to Master Integration Pipeline
    API->>ML: Evaluate Customer Churn Probability (P=0.67)
    ML-->>API: Churn Risk: HIGH
    API->>XAI: Compute Local Feature Attributions
    XAI-->>API: Top Driver: Low License Utilization (-34%)
    API->>RAG: Retrieve Enterprise Retention Playbook
    RAG-->>API: Playbook Context & Step-by-Step Remediation Plan
    API->>DB: Record Immutable Action in Audit Log
    API-->>Edge: Deliver Unified Analysis & Playbook Response
    Edge-->>User: Render Interactive Visual Forecast & Copilot Guidance
```
