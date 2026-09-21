import json
import logging
from typing import Dict, Any
from app.agents.state import ProposalGraphState, OutlineSpec, SectionOutlineItem
from app.core.llm import call_llm_json

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are an Enterprise Bid Director and Proposal Architect.
Your role is to formulate the proposal structure, Table of Contents, and strategic narrative tailored to the client's RFP requirements.

Return a valid JSON object matching this schema:
{
  "strategic_theme": "High-level win theme (e.g. Next-Gen Scalability, Frictionless Modernization, Zero-Trust Architecture)",
  "table_of_contents": [
    {
      "id": "executive_summary",
      "title": "1. Executive Summary",
      "purpose": "State the strategic context, value proposition, and key executive takeaways",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    },
    {
      "id": "technical_architecture",
      "title": "2. Proposed Technical Architecture",
      "purpose": "Define modern architectural design, system components, tech stack, and scalability",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    },
    {
      "id": "deliverables",
      "title": "3. Scope & Key Deliverables",
      "purpose": "Break down delivery into phased milestones with tangible outputs",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    },
    {
      "id": "pricing",
      "title": "4. Commercial & Milestone Investment",
      "purpose": "Provide clear pricing breakdown, milestone schedule, and payment governance",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    }
  ]
}"""


def plan_sections(state: ProposalGraphState) -> Dict[str, Any]:
    """Node: Generate table of contents and section outline."""
    reqs = state.get("requirements", {})
    client_name = state.get("client_name") or reqs.get("client_name", "Enterprise Client")
    project_title = state.get("project_title") or reqs.get("project_title", "Enterprise Solution Proposal")

    prompt = f"""Design the Proposal Outline & Table of Contents for:
Client: {client_name}
Project Title: {project_title}

Extracted Requirements:
- Problem Statement: {reqs.get('problem_statement', '')}
- Key Objectives: {json.dumps(reqs.get('key_objectives', []))}
- Scope Items: {json.dumps(reqs.get('scope_items', []))}
- Compliance / Constraints: {json.dumps(reqs.get('constraints_and_compliance', []))}
- Timeline/Budget: {reqs.get('budget_or_timeline_notes', '')}

Provide the structured proposal plan JSON."""

    try:
        plan_data = call_llm_json(prompt, system_prompt=PLANNER_SYSTEM_PROMPT)
        outline_obj = OutlineSpec(**plan_data)
        return {
            "outline": outline_obj.model_dump(),
            "status": "sections_planned",
        }
    except Exception as e:
        logger.error(f"Section planner node failure: {e}")
        default_outline = OutlineSpec(
            strategic_theme="Scalable Enterprise Modernization & Excellence",
            table_of_contents=[
                SectionOutlineItem(
                    id="executive_summary",
                    title="1. Executive Summary",
                    purpose="Executive overview of business alignment, pain points, and core value proposition",
                    key_points=["Client challenges", "Tailored solution", "Expected business ROI"],
                ),
                SectionOutlineItem(
                    id="technical_architecture",
                    title="2. Proposed Technical Architecture",
                    purpose="Technical specification, components, security, and cloud scalability",
                    key_points=["High-level architecture", "Core technology stack", "Enterprise security compliance"],
                ),
                SectionOutlineItem(
                    id="deliverables",
                    title="3. Scope & Key Deliverables",
                    purpose="Phased implementation breakdown and concrete deliverables",
                    key_points=["Phase 1: Discovery & Architecture", "Phase 2: Core Engineering", "Phase 3: Deployment & Handover"],
                ),
                SectionOutlineItem(
                    id="pricing",
                    title="4. Commercial & Milestone Investment",
                    purpose="Transparent milestone pricing and payment schedule",
                    key_points=["Milestone pricing", "Payment terms", "Assumptions"],
                ),
            ],
        )
        return {
            "outline": default_outline.model_dump(),
            "errors": [f"Section planner fallback applied: {str(e)}"],
            "status": "sections_planned_fallback",
        }
