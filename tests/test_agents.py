import pytest
from app.agents.state import ProposalGraphState
from app.agents.extractor import extract_requirements
from app.agents.section_planner import plan_sections
from app.agents.writers import write_sections
from app.agents.reviewer import review_proposal
from app.agents.graph import build_proposal_graph, proposal_graph


SAMPLE_RFP_TEXT = """
RFP: Cloud Modernization & Distributed Architecture
Client: Acme Corp
We need to migrate our legacy monolithic order processing system to a Kubernetes-based microservices architecture.
Requirements:
1. RESTful and asynchronous event-driven services.
2. High availability with 99.95% uptime.
3. SOC2 compliance and encryption at rest.
Timeline: 12 weeks. Budget target: $100,000 USD.
"""


def test_graph_structure():
    """Verify LangGraph compilation and registered nodes."""
    graph = build_proposal_graph()
    assert graph is not None
    # Verify graph can be invoked
    assert hasattr(proposal_graph, "ainvoke")


def test_extractor_node():
    """Test extractor agent extracts structured requirements."""
    state: ProposalGraphState = {
        "raw_input": SAMPLE_RFP_TEXT,
        "client_name": "Acme Corp",
        "project_title": "Cloud Modernization Architecture",
    }
    result = extract_requirements(state)
    assert "requirements" in result
    reqs = result["requirements"]
    assert reqs["client_name"] == "Acme Corp"
    assert "problem_statement" in reqs
    assert len(reqs.get("scope_items", [])) > 0


def test_section_planner_node():
    """Test section planner produces outline and table of contents."""
    state: ProposalGraphState = {
        "requirements": {
            "client_name": "Acme Corp",
            "project_title": "Cloud Modernization Architecture",
            "problem_statement": "Legacy system scalability bottleneck",
            "key_objectives": ["Modernize stack", "Improve uptime"],
            "scope_items": ["Containerization", "API Gateway", "Data migration"],
            "constraints_and_compliance": ["SOC2"],
            "budget_or_timeline_notes": "12 weeks, $100k",
        }
    }
    result = plan_sections(state)
    assert "outline" in result
    toc = result["outline"].get("table_of_contents", [])
    assert len(toc) >= 4


def test_writers_node():
    """Test writer agents draft all required sections."""
    state: ProposalGraphState = {
        "client_name": "Acme Corp",
        "project_title": "Cloud Modernization Architecture",
        "company_name": "ProposalCraft Solutions",
        "currency": "USD",
        "requirements": {
            "client_name": "Acme Corp",
            "project_title": "Cloud Modernization Architecture",
            "problem_statement": "Scalability bottlenecks",
            "key_objectives": ["Improve throughput", "Reduce downtime"],
            "scope_items": ["Microservices", "Event Streaming"],
            "constraints_and_compliance": ["SOC2"],
            "budget_or_timeline_notes": "12 weeks, $100,000",
        },
    }
    result = write_sections(state)
    assert "sections" in result
    sec = result["sections"]
    assert "executive_summary" in sec
    assert "technical_architecture" in sec
    assert "deliverables" in sec
    assert "pricing" in sec

    # Verify Pricing contains milestones and positive total
    pricing = sec["pricing"]
    assert pricing["total_investment"] > 0
    assert len(pricing["milestones"]) > 0


def test_reviewer_node():
    """Test reviewer agent performs compliance audit."""
    state: ProposalGraphState = {
        "client_name": "Acme Corp",
        "project_title": "Cloud Modernization Architecture",
        "requirements": {
            "key_objectives": ["Uptime"],
            "scope_items": ["Microservices"],
            "constraints_and_compliance": ["SOC2"],
        },
        "sections": {
            "executive_summary": {"challenge": "High latency", "proposed_solution": "Modern APIs"},
            "deliverables": {"phases": [{"phase": "P1"}]},
            "pricing": {"currency": "USD", "total_investment": 100000},
        },
    }
    result = review_proposal(state)
    assert "review_feedback" in result
    feedback = result["review_feedback"]
    assert feedback["compliance_score"] >= 0
    assert feedback["tone_score"] >= 0
    assert "review_notes" in feedback
