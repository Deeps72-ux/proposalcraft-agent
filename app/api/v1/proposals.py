import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, Body, status
from pydantic import BaseModel, Field

from app.core.database import db
from app.core.parser import extract_text_from_upload
from app.agents.graph import run_proposal_generation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/proposals", tags=["Proposals"])


class GenerateProposalJSONRequest(BaseModel):
    rfp_text: str = Field(..., description="Raw RFP text or client tender scope")
    client_name: Optional[str] = Field(default=None, description="Client or organization name")
    project_title: Optional[str] = Field(default=None, description="Proposal project title")
    company_name: Optional[str] = Field(default=None, description="Submitting company/agency name")
    currency: Optional[str] = Field(default="USD", description="Commercial currency code")


class UpdateSectionRequest(BaseModel):
    section_name: str = Field(..., description="Section key (e.g., executive_summary, technical_architecture, deliverables, pricing)")
    content: Any = Field(..., description="Updated section data object or dictionary")


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_proposal_endpoint(request: Request):
    """Generate a structured, executive-ready proposal from raw text or uploaded PDF.

    Accepts either application/json body or multipart/form-data file upload.
    """
    input_text = ""
    filename = None
    final_client = None
    final_title = None
    final_company = None
    final_currency = "USD"

    content_type = request.headers.get("content-type", "").lower()

    if "multipart/form-data" in content_type:
        form = await request.form()
        file = form.get("file")
        if file and hasattr(file, "read") and getattr(file, "filename", None):
            filename = file.filename
            content = await file.read()
            extracted, _ = extract_text_from_upload(content, filename=filename)
            input_text = extracted
        
        form_rfp = form.get("rfp_text")
        if not input_text and form_rfp:
            input_text = str(form_rfp).strip()

        final_client = form.get("client_name") or None
        final_title = form.get("project_title") or None
        final_company = form.get("company_name") or None
        final_currency = form.get("currency") or "USD"
    else:
        try:
            body = await request.json()
            input_text = (body.get("rfp_text") or "").strip()
            final_client = body.get("client_name")
            final_title = body.get("project_title")
            final_company = body.get("company_name")
            final_currency = body.get("currency") or "USD"
        except Exception:
            # Fallback if form data without explicit multipart header
            form = await request.form()
            input_text = (form.get("rfp_text") or "").strip()
            final_client = form.get("client_name") or None
            final_title = form.get("project_title") or None
            final_company = form.get("company_name") or None
            final_currency = form.get("currency") or "USD"

    if not input_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No RFP content provided. Please upload a PDF/text file or provide rfp_text in request body.",
        )

    try:
        # Run autonomous LangGraph agent workflow
        final_state = await run_proposal_generation(
            rfp_text=input_text,
            client_name=final_client,
            project_title=final_title,
            filename=filename,
            company_name=final_company,
            currency=final_currency,
        )

        # Save to database
        proposal_id = await db.save_proposal(final_state)
        stored_proposal = await db.get_proposal(proposal_id)

        return {
            "id": proposal_id,
            "status": "completed",
            "message": "Proposal successfully generated and reviewed by agentic pipeline.",
            "proposal": stored_proposal,
        }
    except Exception as e:
        logger.error(f"Proposal generation pipeline failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Proposal generation failed: {str(e)}",
        )


@router.get("", response_model=List[Dict[str, Any]])
async def list_proposals_endpoint(limit: int = 50):
    """List recently generated proposals."""
    return await db.list_proposals(limit=limit)


@router.get("/{id}")
async def get_proposal_endpoint(id: str):
    """Retrieve full proposal by ID."""
    proposal = await db.get_proposal(id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID '{id}' not found.",
        )
    return proposal


@router.put("/{id}/section")
async def update_proposal_section_endpoint(id: str, payload: UpdateSectionRequest):
    """Edit a specific proposal section before final document export."""
    updated = await db.update_proposal_section(
        proposal_id=id,
        section_name=payload.section_name,
        content=payload.content,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID '{id}' not found.",
        )
    return {
        "id": id,
        "status": "updated",
        "message": f"Section '{payload.section_name}' updated successfully.",
        "proposal": updated,
    }
