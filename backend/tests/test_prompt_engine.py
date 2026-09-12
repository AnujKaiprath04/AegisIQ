import pytest
from fastapi.testclient import TestClient
from app.prompt_service.formatter import PromptFormatter
from app.prompt_service.types import FewShotExample


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_template_variable_interpolation():
    template = "Welcome to {{company_name}}! Current ARR: {{arr}}."
    rendered = PromptFormatter.interpolate(template, {"company_name": "AegisIQ", "arr": "$24.8M"})
    assert rendered == "Welcome to AegisIQ! Current ARR: $24.8M."

    # Missing variable fallback
    rendered_missing = PromptFormatter.interpolate(template, {"company_name": "AegisIQ"})
    assert "[arr]" in rendered_missing


def test_few_shot_attachment():
    text = "Extract entity names."
    examples = [
        FewShotExample(user_input="Alice in Finance", ideal_output="Name: Alice, Dept: Finance"),
    ]
    with_shots = PromptFormatter.attach_few_shots(text, examples)
    assert "Few-Shot Reference Exemplars" in with_shots
    assert "Alice in Finance" in with_shots


def test_list_prompt_templates(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/prompts/templates",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    templates = res.json()
    assert len(templates) >= 8
    names = [t["name"] for t in templates]
    assert "SYSTEM_CORE_COPILOT" in names
    assert "BUSINESS_KPI_ANALYZER" in names
    assert "NL_TO_SQL_SYNTHESIZER" in names


def test_render_prompt_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/prompts/render",
        json={
            "template_name": "BUSINESS_KPI_ANALYZER",
            "variables": {
                "kpi_name": "Gross Profit Margin",
                "current_value": "68.4%",
                "target_value": "65.0%",
                "variance": "+5.2%",
                "context_passages": "Cloud compute optimization reduced hosting expenses.",
            },
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "Gross Profit Margin" in data["rendered_prompt"]
    assert data["estimated_tokens"] > 0


def test_register_custom_prompt_template(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/prompts/templates",
        json={
            "name": "CUSTOM_COST_AUDIT_PROMPT",
            "category": "BUSINESS",
            "version": "v1.0",
            "template_text": "Audit AWS cloud infrastructure line items for {{account_id}} and highlight any cost anomalies.",
            "input_variables": ["account_id"],
            "description": "Custom prompt for automated cloud infrastructure cost audits.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    assert res.json()["name"] == "CUSTOM_COST_AUDIT_PROMPT"


def test_prompt_playground_execution(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/prompts/test-playground",
        json={
            "template_name": "DOCUMENT_EXECUTIVE_SUMMARY",
            "variables": {
                "document_title": "ISO 27001 Security Standard",
                "department": "SECURITY",
                "document_text": "Section 9.2: Access control requires hardware MFA enforcement.",
            },
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "ISO 27001" in data["rendered_prompt"]
    assert len(data["generated_output"]) > 0
    assert data["latency_ms"] > 0
