import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import db

client = TestClient(app)


def test_health_check():
    """Verify /health returns 200 OK and expected keys."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "llm_model" in data


def test_list_templates():
    """Verify /api/v1/templates returns list of brand themes."""
    response = client.get("/api/v1/templates")
    assert response.status_code == 200
    themes = response.json()
    assert isinstance(themes, list)
    assert len(themes) >= 1
    assert "primary_color" in themes[0]


@pytest.mark.asyncio
async def test_proposal_lifecycle_and_exports():
    """End-to-end test of proposal creation, retrieval, section update, and downloads."""
    # 1. Pre-seed a proposal in database for fast, deterministic testing
    test_proposal = {
        "client_name": "Globex Corporation",
        "project_title": "Enterprise Cloud Architecture",
        "company_name": "ProposalCraft Solutions",
        "currency": "USD",
        "requirements": {
            "client_name": "Globex Corporation",
            "project_title": "Enterprise Cloud Architecture",
            "problem_statement": "Scalability bottlenecks in monolithic core.",
            "key_objectives": ["Modernize stack", "Improve uptime"],
            "scope_items": ["Microservices", "Event Streaming"],
            "constraints_and_compliance": ["SOC2"],
            "budget_or_timeline_notes": "12 weeks, $120,000",
        },
        "sections": {
            "executive_summary": {
                "title": "1. Executive Summary",
                "challenge": "Monolithic architecture limits scale.",
                "proposed_solution": "Cloud-native microservices.",
                "strategic_value": "40% cost reduction.",
                "highlights": ["High availability", "Automated deployment"],
            },
            "technical_architecture": {
                "title": "2. Proposed Technical Architecture",
                "overview": "Asynchronous microservices running on AWS EKS.",
                "components": [
                    {"name": "API Gateway", "tech_stack": "FastAPI", "description": "Ingress router"}
                ],
                "security_and_compliance": "SOC2 Type II, AES-256.",
                "scalability_and_resilience": "Multi-region autoscaling.",
            },
            "deliverables": {
                "title": "3. Scope & Key Deliverables",
                "phases": [
                    {
                        "phase": "Phase 1: Architecture",
                        "duration": "Weeks 1-3",
                        "deliverables": ["Blueprint"],
                        "outcome": "Architecture sign-off",
                    }
                ],
            },
            "pricing": {
                "title": "4. Commercial & Milestone Investment",
                "currency": "USD",
                "milestones": [
                    {
                        "milestone": "Milestone 1",
                        "deliverable": "Architecture",
                        "timeline": "Week 3",
                        "amount": 30000.0,
                        "percentage": "25%",
                    }
                ],
                "total_investment": 30000.0,
                "payment_terms": "Net 30 days",
                "assumptions": ["Client AWS account"],
            },
        },
        "review_feedback": {
            "compliance_score": 98,
            "tone_score": 96,
            "review_notes": "Fully verified and approved.",
        },
    }

    pid = await db.save_proposal(test_proposal)
    assert pid is not None

    # 2. Test GET proposal by ID
    get_res = client.get(f"/api/v1/proposals/{pid}")
    assert get_res.status_code == 200
    assert get_res.json()["client_name"] == "Globex Corporation"

    # 3. Test PUT update section
    update_res = client.put(
        f"/api/v1/proposals/{pid}/section",
        json={
            "section_name": "executive_summary",
            "content": {
                "title": "1. Executive Summary",
                "challenge": "Updated challenge text for testing.",
                "proposed_solution": "Updated solution.",
                "strategic_value": "Updated value.",
                "highlights": ["Updated highlight"],
            },
        },
    )
    assert update_res.status_code == 200
    updated_body = update_res.json()
    assert updated_body["proposal"]["sections"]["executive_summary"]["challenge"] == "Updated challenge text for testing."

    # 4. Test Export PDF
    pdf_res = client.get(f"/api/v1/proposals/{pid}/export/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF")

    # 5. Test Export DOCX
    docx_res = client.get(f"/api/v1/proposals/{pid}/export/docx")
    assert docx_res.status_code == 200
    assert "wordprocessingml" in docx_res.headers["content-type"]
    assert docx_res.content.startswith(b"PK")

    # 6. Test Export PPTX
    pptx_res = client.get(f"/api/v1/proposals/{pid}/export/pptx")
    assert pptx_res.status_code == 200
    assert "presentationml" in pptx_res.headers["content-type"]
    assert pptx_res.content.startswith(b"PK")

    # 7. Test invalid export format
    inv_res = client.get(f"/api/v1/proposals/{pid}/export/invalidformat")
    assert inv_res.status_code == 400

    # 8. Test export non-existent proposal
    missing_res = client.get("/api/v1/proposals/non-existent-uuid/export/pdf")
    assert missing_res.status_code == 404
