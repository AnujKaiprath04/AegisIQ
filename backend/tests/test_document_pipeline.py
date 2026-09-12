import pytest
from fastapi.testclient import TestClient
from app.document_service.cleaner import TextCleaner
from app.document_service.parsers import DocumentParserFactory
from app.document_service.chunker import RecursiveSemanticChunker


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_text_cleaner_and_normalizer():
    dirty_text = "  AegisIQ\r\n\r\n\r\n\r\nEnterprise   AI   Platform. \x00\x08Zero-Trust  Security.  "
    cleaned = TextCleaner.clean_text(dirty_text)
    assert "\x00" not in cleaned
    assert "   " not in cleaned
    assert "AegisIQ\n\nEnterprise AI Platform. Zero-Trust Security." == cleaned


def test_multi_format_parsers():
    # Markdown
    md_parser = DocumentParserFactory.get_parser("MARKDOWN")
    md_text = md_parser.parse(b"# Security Standard\nSection 1: Access Control.", "standard.md")
    assert "Security Standard" in md_text

    # CSV
    csv_parser = DocumentParserFactory.get_parser("CSV")
    csv_data = b"Month,ARR,Margin\nJan,24M,68%\nFeb,25M,69%"
    csv_text = csv_parser.parse(csv_data, "financials.csv")
    assert "Month: Jan" in csv_text or "ARR: 24M" in csv_text


def test_recursive_semantic_chunker():
    long_text = (
        "## ISO 27001 Security Overview\n\n"
        "Access control policies must be strictly enforced across all cloud infrastructure boundaries. "
        "Every engineer must authenticate using hardware multi-factor security keys.\n\n"
        "## Incident Response Protocol\n\n"
        "In the event of a security anomaly, edge ingress gateways will automatically isolate the suspect subnet. "
        "SOC analysts are notified via high-priority Slack webhook alerts within 30 seconds."
    )
    chunker = RecursiveSemanticChunker(chunk_size=150, chunk_overlap=30)
    chunks = chunker.chunk_text(long_text)
    assert len(chunks) >= 2
    for c in chunks:
        assert c.token_count > 0
        assert c.char_length <= 250  # Boundary buffer


def test_direct_parse_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/pipeline/parse-text",
        json={
            "text": "Paragraph 1: Enterprise Data Governance.\n\nParagraph 2: Role-based Authorization Matrix.\n\nParagraph 3: Cloud Telemetry.",
            "chunk_size": 200,
            "chunk_overlap": 40,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_chunks"] >= 1
    assert len(data["chunks"]) >= 1


def test_end_to_end_document_processing_pipeline(client: TestClient):
    token = get_auth_token(client)
    
    # 1. Get first document ID
    docs_res = client.get("/api/v1/ai/knowledge/documents", headers={"Authorization": f"Bearer {token}"})
    doc_id = docs_res.json()[0]["id"]

    # 2. Process document
    proc_res = client.post(
        f"/api/v1/ai/pipeline/process/{doc_id}?chunk_size=300&chunk_overlap=50",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert proc_res.status_code == 200
    data = proc_res.json()
    assert data["status"] == "INDEXED"
    assert data["total_chunks_created"] > 0
    assert data["processing_latency_ms"] > 0

    # 3. Check status
    stat_res = client.get(
        f"/api/v1/ai/pipeline/status/{doc_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert stat_res.status_code == 200
    assert stat_res.json()["status"] == "INDEXED"
