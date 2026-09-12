import json
import random
from locust import HttpUser, between, task


class AegisIQEnterpriseUser(HttpUser):
    """Simulates realistic enterprise user traffic across Authentication, BI, RAG, and ML APIs."""

    wait_time = between(1, 3)
    token = None

    def on_start(self):
        """Authenticate user on start and obtain JWT bearer token."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "admin@aegisiq.com", "password": "Admin@12345"},
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

    @task(4)
    def query_bi_dashboards(self):
        """Simulate high-frequency BI dashboard metric retrieval."""
        self.client.get("/api/v1/bi/kpis/summary", headers=self.headers)
        self.client.get("/api/v1/bi/kpis/variance", headers=self.headers)

    @task(3)
    def query_predictive_ml(self):
        """Simulate predictive ML churn and revenue forecasting."""
        self.client.post(
            "/api/v1/ml/predictions/churn",
            json={
                "account_id": f"ACC-LOAD-{random.randint(100, 999)}",
                "company_name": "Benchmark Corp",
                "license_utilization_pct": random.uniform(20.0, 90.0),
                "support_tickets_last_30d": random.randint(1, 15),
                "nps_score": random.randint(2, 9),
                "days_to_renewal": 60,
            },
            headers=self.headers,
        )

    @task(2)
    def query_rag_copilot(self):
        """Simulate enterprise AI Copilot prompt queries."""
        self.client.post(
            "/api/v1/rag/query",
            json={
                "query": "What are our approved enterprise customer retention playbooks?",
                "top_k": 3,
            },
            headers=self.headers,
        )

    @task(1)
    def get_system_health(self):
        """Simulate lightweight health monitoring probe."""
        self.client.get("/health")
