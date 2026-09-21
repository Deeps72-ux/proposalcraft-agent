import json
import logging
from typing import Dict, Any
from app.agents.state import (
    ProposalGraphState,
    ExecutiveSummarySection,
    TechnicalArchitectureSection,
    DeliverablesSection,
    PhaseDeliverable,
    PricingSection,
    PricingMilestone,
    ProposalSections,
)
from app.core.llm import call_llm_json

logger = logging.getLogger(__name__)


def write_executive_summary(state: ProposalGraphState) -> ExecutiveSummarySection:
    reqs = state.get("requirements", {})
    client = state.get("client_name") or reqs.get("client_name", "Enterprise Client")
    company = state.get("company_name", "ProposalCraft Solutions")
    project = state.get("project_title") or reqs.get("project_title", "Enterprise Solution")

    prompt = f"""Write the Executive Summary for this enterprise proposal.
Client: {client}
Vendor / Service Provider: {company}
Project Title: {project}

Client Context & Requirements:
- Problem: {reqs.get('problem_statement', '')}
- Key Objectives: {json.dumps(reqs.get('key_objectives', []))}
- Scope Summary: {json.dumps(reqs.get('scope_items', []))}

Respond with pure JSON matching this exact structure:
{{
  "title": "1. Executive Summary",
  "challenge": "A compelling 2-3 sentence summary of the client's strategic challenge and opportunity.",
  "proposed_solution": "A 2-3 sentence overview of the tailored solution provided by {company}.",
  "strategic_value": "Expected return on investment, operational efficiency gains, and long-term business value.",
  "highlights": [
    "Highlight 1: Core differentiator or value delivered",
    "Highlight 2: Strategic alignment with client roadmap",
    "Highlight 3: Risk mitigation and enterprise assurance"
  ]
}}"""

    try:
        data = call_llm_json(prompt, system_prompt="You are an Executive Proposal Writer crafting winning C-level business proposals.")
        return ExecutiveSummarySection(**data)
    except Exception as e:
        logger.warning(f"Executive summary write error: {e}")
        return ExecutiveSummarySection(
            title="1. Executive Summary",
            challenge=f"{client} faces the critical imperative to modernize operational systems, streamline workflows, and ensure enterprise-grade resilience.",
            proposed_solution=f"{company} proposes an integrated, modern solution tailored to {client}'s operational standards and strategic growth objectives.",
            strategic_value="Significantly accelerates time-to-market, reduces operational overhead by up to 35%, and establishes robust architectural standards.",
            highlights=[
                "Turnkey architectural design aligned with industry standards",
                "Proven delivery track record with predictable milestones",
                "Zero-compromise security and governance framework"
            ]
        )


def write_technical_architecture(state: ProposalGraphState) -> TechnicalArchitectureSection:
    reqs = state.get("requirements", {})
    client = state.get("client_name") or reqs.get("client_name", "Enterprise Client")
    company = state.get("company_name", "ProposalCraft Solutions")
    project = state.get("project_title") or reqs.get("project_title", "Enterprise Solution")

    prompt = f"""Write the Proposed Technical Architecture section for this proposal.
Client: {client}
Vendor: {company}
Project: {project}

Scope & Tech Requirements:
- Scope: {json.dumps(reqs.get('scope_items', []))}
- Compliance & Constraints: {json.dumps(reqs.get('constraints_and_compliance', []))}

Respond with pure JSON matching this exact structure:
{{
  "title": "2. Proposed Technical Architecture",
  "overview": "Detailed overview of the end-to-end system architecture, modular design, and data flows.",
  "components": [
    {{
      "name": "API & Ingestion Layer",
      "description": "High-throughput asynchronous gateways and protocol adapters.",
      "tech_stack": "FastAPI, Python 3.11, Pydantic, Redis"
    }},
    {{
      "name": "Processing & Intelligence Engine",
      "description": "Stateful agent orchestration and LLM inference pipelines.",
      "tech_stack": "LangGraph, Groq LLM Inference, PyTorch"
    }},
    {{
      "name": "Data Persistence & Storage",
      "description": "Relational transactional storage with vector indexing.",
      "tech_stack": "PostgreSQL 16, pgvector, S3-Compatible Blob Storage"
    }},
    {{
      "name": "Document Layout & Compilation Engine",
      "description": "Multi-format rendering and publication pipeline.",
      "tech_stack": "ReportLab, python-docx, python-pptx"
    }}
  ],
  "security_and_compliance": "Comprehensive enterprise security including TLS 1.3 encryption in-transit, AES-256 at-rest, OAuth2/OIDC role-based access control (RBAC), and strict SOC2 / GDPR alignment.",
  "scalability_and_resilience": "Cloud-native containerized architecture supporting horizontal autoscaling, 99.95% availability SLA, automated disaster recovery, and multi-region read replicas."
}}"""

    try:
        data = call_llm_json(prompt, system_prompt="You are a Principal Enterprise Solutions Architect writing proposal technical architectures.")
        return TechnicalArchitectureSection(**data)
    except Exception as e:
        logger.warning(f"Technical architecture write error: {e}")
        return TechnicalArchitectureSection(
            title="2. Proposed Technical Architecture",
            overview="The proposed architecture utilizes a microservices-based, event-driven pattern designed for high availability, enterprise security, and seamless integration.",
            components=[
                {
                    "name": "Application Gateway & API",
                    "description": "Unified REST & event routing layer with rate limiting and authentication.",
                    "tech_stack": "FastAPI, Python 3.11, Pydantic"
                },
                {
                    "name": "Agentic Orchestration Core",
                    "description": "Stateful workflow management and LLM inference pipelines.",
                    "tech_stack": "LangGraph, Groq"
                },
                {
                    "name": "Document Generation Services",
                    "description": "High-fidelity rendering of PDF, Word DOCX, and PowerPoint pitch decks.",
                    "tech_stack": "ReportLab, python-docx, python-pptx"
                }
            ],
            security_and_compliance="Full adherence to enterprise security benchmarks including AES-256 encryption at-rest, TLS 1.3 in-transit, and continuous auditing.",
            scalability_and_resilience="Containerized deployment with auto-scaling capabilities and sub-second recovery objectives."
        )


def write_deliverables(state: ProposalGraphState) -> DeliverablesSection:
    reqs = state.get("requirements", {})
    client = state.get("client_name") or reqs.get("client_name", "Enterprise Client")
    scope = reqs.get("scope_items", [])
    timeline = reqs.get("budget_or_timeline_notes", "12-16 weeks")

    prompt = f"""Write the Scope & Key Deliverables section for this proposal.
Client: {client}
Scope Items: {json.dumps(scope)}
Timeline Guidance: {timeline}

Respond with pure JSON matching this exact structure:
{{
  "title": "3. Scope & Key Deliverables",
  "phases": [
    {{
      "phase": "Phase 1: Discovery, Architecture & Design",
      "duration": "Weeks 1 - 3",
      "deliverables": [
        "Architecture Design Document (ADD) & API Specifications",
        "Security, Compliance & Data Governance Blueprint",
        "Detailed Sprint Backlog & Acceptance Criteria"
      ],
      "outcome": "Sign-off on technical architecture and foundational development environment."
    }},
    {{
      "phase": "Phase 2: Core Engineering & Model Integration",
      "duration": "Weeks 4 - 8",
      "deliverables": [
        "Core workflow engine and API endpoints implementation",
        "LangGraph state machine and Groq LLM pipelines",
        "Automated unit and integration test suite"
      ],
      "outcome": "Functioning MVP demonstrating automated proposal synthesis."
    }},
    {{
      "phase": "Phase 3: Multi-Format Renderers & UI",
      "duration": "Weeks 9 - 12",
      "deliverables": [
        "ReportLab PDF, python-docx DOCX, and python-pptx export engines",
        "Web application dashboard & export controllers",
        "End-to-end automated regression testing"
      ],
      "outcome": "Production-ready system capable of publishing all output document formats."
    }},
    {{
      "phase": "Phase 4: UAT, Hardening & Production Rollout",
      "duration": "Weeks 13 - 14",
      "deliverables": [
        "User Acceptance Testing (UAT) sign-off report",
        "Deployment runbooks, CI/CD pipelines, and monitoring dashboards",
        "Administrator and user training sessions"
      ],
      "outcome": "Full production deployment with ongoing warranty support."
    }}
  ]
}}"""

    try:
        data = call_llm_json(prompt, system_prompt="You are a Senior Technical Project Manager writing delivery roadmaps.")
        return DeliverablesSection(**data)
    except Exception as e:
        logger.warning(f"Deliverables write error: {e}")
        return DeliverablesSection(
            title="3. Scope & Key Deliverables",
            phases=[
                PhaseDeliverable(
                    phase="Phase 1: Discovery & Architecture",
                    duration="Weeks 1-3",
                    deliverables=["System Architecture Blueprint", "Security Baseline Review", "Sprint Backlog"],
                    outcome="Architecture sign-off and environment configuration."
                ),
                PhaseDeliverable(
                    phase="Phase 2: Core Implementation",
                    duration="Weeks 4-8",
                    deliverables=["Core API Services", "Agentic Pipelines", "Data Pipeline Integration"],
                    outcome="Working prototype with validated core workflows."
                ),
                PhaseDeliverable(
                    phase="Phase 3: Testing & Deployment",
                    duration="Weeks 9-12",
                    deliverables=["UAT Testing Report", "Production Deployment", "Operations Runbook"],
                    outcome="Enterprise rollout and handover."
                )
            ]
        )


def write_pricing(state: ProposalGraphState) -> PricingSection:
    reqs = state.get("requirements", {})
    currency = state.get("currency", "USD")

    prompt = f"""Write the Commercial & Milestone Investment section for this proposal.
Currency: {currency}
Requirements Summary:
- Scope: {json.dumps(reqs.get('scope_items', []))}
- Timeline/Budget Notes: {reqs.get('budget_or_timeline_notes', '')}

Provide realistic enterprise figures.
Respond with pure JSON matching this exact structure:
{{
  "title": "4. Commercial & Milestone Investment",
  "currency": "{currency}",
  "milestones": [
    {{
      "milestone": "Milestone 1: Project Kickoff & Architecture Approval",
      "deliverable": "Approved Architecture Blueprint & Development Environment Setup",
      "timeline": "Month 1 (End of Week 3)",
      "amount": 25000,
      "percentage": "25%"
    }},
    {{
      "milestone": "Milestone 2: Core Platform & Pipeline Completion",
      "deliverable": "Functional API, Agent Pipelines, and Intermediate Beta Review",
      "timeline": "Month 2 (End of Week 8)",
      "amount": 40000,
      "percentage": "40%"
    }},
    {{
      "milestone": "Milestone 3: Multi-Format Export Engine & UI",
      "deliverable": "Integrated Document Renderers, Web UI, and Test Coverage",
      "timeline": "Month 3 (End of Week 12)",
      "amount": 25000,
      "percentage": "25%"
    }},
    {{
      "milestone": "Milestone 4: Final UAT Acceptance & Deployment",
      "deliverable": "Production Rollout, Documentation & Training Handover",
      "timeline": "Month 4 (End of Week 14)",
      "amount": 10000,
      "percentage": "10%"
    }}
  ],
  "total_investment": 100000,
  "payment_terms": "Net 30 days upon formal delivery and sign-off of milestone deliverables.",
  "assumptions": [
    "Pricing reflects full lifecycle software engineering, architecture, QA, and initial warranty.",
    "Third-party cloud infrastructure and LLM token costs billed directly to client account.",
    "Additional scope changes governed under standard Change Request Procedure."
  ]
}}"""

    try:
        data = call_llm_json(prompt, system_prompt="You are an Enterprise Commercial Bid Director structuring transparent commercial models.")
        # Ensure total_investment matches sum if discrepancy exists
        milestones = data.get("milestones", [])
        calc_total = sum(float(m.get("amount", 0)) for m in milestones)
        if calc_total > 0:
            data["total_investment"] = calc_total
        return PricingSection(**data)
    except Exception as e:
        logger.warning(f"Pricing write error: {e}")
        return PricingSection(
            title="4. Commercial & Milestone Investment",
            currency=currency,
            milestones=[
                PricingMilestone(
                    milestone="Milestone 1: Architecture & Design",
                    deliverable="System Architecture Specification",
                    timeline="Week 3",
                    amount=20000.0,
                    percentage="25%"
                ),
                PricingMilestone(
                    milestone="Milestone 2: Core Platform Implementation",
                    deliverable="Working Pipeline & Integration",
                    timeline="Week 8",
                    amount=36000.0,
                    percentage="45%"
                ),
                PricingMilestone(
                    milestone="Milestone 3: Final Delivery & Deployment",
                    deliverable="Production Sign-off & Handover",
                    timeline="Week 12",
                    amount=24000.0,
                    percentage="30%"
                )
            ],
            total_investment=80000.0,
            payment_terms="Net 30 days upon milestone acceptance.",
            assumptions=["Includes warranty support for 60 days following production launch."]
        )


def write_sections(state: ProposalGraphState) -> Dict[str, Any]:
    """Node: Parallel Sub-Agents write Executive Summary, Technical Architecture, Deliverables, and Pricing sections."""
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        f_exec = executor.submit(write_executive_summary, state)
        f_arch = executor.submit(write_technical_architecture, state)
        f_deliv = executor.submit(write_deliverables, state)
        f_price = executor.submit(write_pricing, state)

        exec_summary = f_exec.result()
        tech_arch = f_arch.result()
        deliverables = f_deliv.result()
        pricing = f_price.result()

    sections = ProposalSections(
        executive_summary=exec_summary,
        technical_architecture=tech_arch,
        deliverables=deliverables,
        pricing=pricing,
    )

    return {
        "sections": sections.model_dump(),
        "status": "sections_written",
    }

