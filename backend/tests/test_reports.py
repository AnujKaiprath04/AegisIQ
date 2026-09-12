import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "executive@aegisiq.com", password: str = "Exec@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_generate_pdf_and_excel_reports(client: TestClient):
    token = get_auth_token(client)

    # 1. Generate PDF Report
    pdf_req = {
        "title": "Quarterly Executive Briefing",
        "report_type": "EXECUTIVE_SUMMARY",
        "format": "PDF",
        "date_range": "Q1 2026",
    }
    pdf_res = client.post("/api/v1/reports/generate", json=pdf_req, headers={"Authorization": f"Bearer {token}"})
    assert pdf_res.status_code == 201
    pdf_data = pdf_res.json()
    assert pdf_data["format"] == "PDF"
    report_id = pdf_data["id"]

    # Download PDF
    dl_res = client.get(f"/api/v1/reports/{report_id}/download", headers={"Authorization": f"Bearer {token}"})
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert len(dl_res.content) > 500

    # 2. Generate Excel Report
    xls_req = {
        "title": "Financial Audit & Ledger Workbook",
        "report_type": "FINANCIAL_HEALTH",
        "format": "EXCEL",
        "date_range": "Q1 2026",
    }
    xls_res = client.post("/api/v1/reports/generate", json=xls_req, headers={"Authorization": f"Bearer {token}"})
    assert xls_res.status_code == 201
    xls_data = xls_res.json()
    assert xls_data["format"] == "EXCEL"
    xls_id = xls_data["id"]

    # Download Excel
    dl_xls = client.get(f"/api/v1/reports/{xls_id}/download", headers={"Authorization": f"Bearer {token}"})
    assert dl_xls.status_code == 200
    assert "openxmlformats" in dl_xls.headers["content-type"]
