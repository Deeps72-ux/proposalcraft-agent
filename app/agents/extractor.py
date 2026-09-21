import logging
from typing import Dict, Any
from app.agents.state import ProposalGraphState, RequirementSpec
from app.core.llm import call_llm_json

logger = logging.getLogger(__name__)

EXTRACTOR_SYSTEM_PROMPT = """You are an expert Enterprise Proposal Strategist and RFP Analyst.
Your job is to thoroughly analyze the provided client RFP / tender text and extract critical commercial and technical requirements.

You must respond with a JSON object matching this schema:
{
  "client_name": "Name of the client organization (or inferred from RFP)",
  "project_title": "Professional, formal project title",
  "problem_statement": "Concise 2-3 sentence overview of the client's current pain points and challenges",
  "key_objectives": ["List of 3-5 measurable business and technical objectives"],
  "scope_items": ["List of 4-6 specific in-scope capabilities, modules, or services requested"],
  "constraints_and_compliance": ["List of 2-4 compliance standards (e.g., SOC2, GDPR, HIPAA, SLA) or constraints"],
  "budget_or_timeline_notes": "Mentioned or inferred timeline and budget constraints"
}"""


def extract_requirements(state: ProposalGraphState) -> Dict[str, Any]:
    """Node: Parse uploaded RFP text/PDF and extract structured requirements."""
    raw_input = state.get("raw_input", "").strip()
    if not raw_input:
        return {
            "requirements": RequirementSpec().model_dump(),
            "errors": ["No input RFP text provided to extractor"],
            "status": "error_extractor",
        }

    client_override = state.get("client_name")
    title_override = state.get("project_title")

    prompt = f"""Analyze this Client RFP Document and extract structured requirements:

=== CLIENT RFP INPUT ===
{raw_input[:10000]}
========================

Existing Overrides (if any):
- Client Name: {client_override or "Infer from document"}
- Project Title: {title_override or "Infer from document"}

Extract the full requirements JSON according to the required schema."""

    try:
        extracted = call_llm_json(prompt, system_prompt=EXTRACTOR_SYSTEM_PROMPT)
        # Apply overrides if provided by the user
        if client_override:
            extracted["client_name"] = client_override
        if title_override:
            extracted["project_title"] = title_override

        # Validate with Pydantic
        req_obj = RequirementSpec(**extracted)
        return {
            "requirements": req_obj.model_dump(),
            "client_name": req_obj.client_name,
            "project_title": req_obj.project_title,
            "status": "requirements_extracted",
        }
    except Exception as e:
        logger.error(f"Extractor node failure: {e}")
        fallback = RequirementSpec(
            client_name=client_override or "Enterprise Client",
            project_title=title_override or "Enterprise Solution & Transformation Proposal",
            problem_statement=raw_input[:300] + "...",
            key_objectives=["Modernize core system infrastructure", "Enhance performance and security"],
            scope_items=["Architecture design", "Core implementation", "Testing & validation", "Deployment & Handover"],
            constraints_and_compliance=["Industry standard security & uptime SLAs"],
            budget_or_timeline_notes="Standard enterprise delivery timeline",
        )
        return {
            "requirements": fallback.model_dump(),
            "client_name": fallback.client_name,
            "project_title": fallback.project_title,
            "errors": [f"Extractor fallback applied: {str(e)}"],
            "status": "requirements_extracted_fallback",
        }
