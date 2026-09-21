import logging
from typing import Optional, Dict, Any
from langgraph.graph import StateGraph, START, END

from app.agents.state import ProposalGraphState
from app.agents.extractor import extract_requirements
from app.agents.section_planner import plan_sections
from app.agents.writers import write_sections
from app.agents.reviewer import review_proposal
from app.core.config import settings

logger = logging.getLogger(__name__)


def build_proposal_graph() -> StateGraph:
    """Compile the LangGraph state machine for proposal generation."""
    workflow = StateGraph(ProposalGraphState)

    # Register agent nodes
    workflow.add_node("extract_requirements", extract_requirements)
    workflow.add_node("plan_sections", plan_sections)
    workflow.add_node("write_sections", write_sections)
    workflow.add_node("review_proposal", review_proposal)

    # Establish linear synthesis flow
    workflow.add_edge(START, "extract_requirements")
    workflow.add_edge("extract_requirements", "plan_sections")
    workflow.add_edge("plan_sections", "write_sections")
    workflow.add_edge("write_sections", "review_proposal")
    workflow.add_edge("review_proposal", END)

    return workflow.compile()


proposal_graph = build_proposal_graph()


async def run_proposal_generation(
    rfp_text: str,
    client_name: Optional[str] = None,
    project_title: Optional[str] = None,
    filename: Optional[str] = None,
    company_name: Optional[str] = None,
    currency: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute the full agentic proposal generation pipeline asynchronously."""
    initial_state: ProposalGraphState = {
        "raw_input": rfp_text,
        "filename": filename,
        "client_name": client_name,
        "project_title": project_title,
        "company_name": company_name or settings.COMPANY_NAME,
        "currency": currency or settings.DEFAULT_CURRENCY,
        "requirements": {},
        "outline": {},
        "sections": {},
        "review_feedback": {},
        "status": "started",
        "errors": [],
    }

    logger.info("Executing LangGraph Proposal Generation Pipeline...")
    final_state = await proposal_graph.ainvoke(initial_state)
    logger.info(f"LangGraph execution finished with status: {final_state.get('status')}")
    return final_state
