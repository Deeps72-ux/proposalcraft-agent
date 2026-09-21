import logging
from fastapi import APIRouter, HTTPException, Response, status
from app.core.database import db
from app.renderers.pdf_renderer import render_pdf
from app.renderers.docx_renderer import render_docx
from app.renderers.pptx_renderer import render_pptx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/proposals", tags=["Export"])

MIME_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


@router.get("/{id}/export/{format}")
async def export_proposal_endpoint(id: str, format: str):
    """Export a proposal into enterprise PDF, Word DOCX, or PowerPoint PPTX format."""
    fmt = format.lower().strip()
    if fmt not in MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{format}'. Supported formats: pdf, docx, pptx.",
        )

    proposal = await db.get_proposal(id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID '{id}' not found.",
        )

    # Clean filename using client or project name if possible
    clean_title = (proposal.get("project_title") or "Proposal").replace(" ", "_")[:30]
    filename = f"{clean_title}_{id[:8]}.{fmt}"

    try:
        if fmt == "pdf":
            file_bytes = render_pdf(proposal)
        elif fmt == "docx":
            file_bytes = render_docx(proposal)
        elif fmt == "pptx":
            file_bytes = render_pptx(proposal)
        else:
            raise ValueError(f"Unknown format: {fmt}")

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(file_bytes)),
            "Access-Control-Expose-Headers": "Content-Disposition",
        }

        return Response(
            content=file_bytes,
            media_type=MIME_TYPES[fmt],
            headers=headers,
        )
    except Exception as e:
        logger.error(f"Failed to render document format '{fmt}' for proposal {id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document generation error: {str(e)}",
        )
