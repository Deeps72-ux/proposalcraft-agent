import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.router import api_router

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="ProposalCraft API",
    description="Autonomous Business RFP & Document Generation Engine powered by LangGraph, Groq LLM, and ReportLab.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API
app.include_router(api_router)

# Mount Static Files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint validating service availability."""
    return {
        "status": "healthy",
        "service": "proposalcraft-api",
        "version": "1.0.0",
        "llm_model": settings.GROQ_CHAT_MODEL,
        "company_name": settings.COMPANY_NAME,
        "default_currency": settings.DEFAULT_CURRENCY,
    }


@app.get("/", include_in_schema=False)
async def root():
    """Serve the web application frontend."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "ProposalCraft API is running. Visit /docs for API documentation."}
