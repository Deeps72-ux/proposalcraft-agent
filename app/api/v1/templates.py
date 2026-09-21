from typing import Dict, Any, List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/templates", tags=["Templates & Branding"])


class BrandTheme(BaseModel):
    id: str
    name: str
    primary_color: str
    accent_color: str
    background_color: str
    font_family: str
    description: str


THEMES: List[BrandTheme] = [
    BrandTheme(
        id="executive_blue",
        name="Executive Blue",
        primary_color="#0F172A",
        accent_color="#2563EB",
        background_color="#F8FAFC",
        font_family="Helvetica / Arial",
        description="Authoritative, corporate blue & slate palette for C-level proposals",
    ),
    BrandTheme(
        id="tech_indigo",
        name="Modern Indigo",
        primary_color="#1E1B4B",
        accent_color="#6366F1",
        background_color="#F5F3FF",
        font_family="Arial",
        description="High-tech SaaS and cloud architecture theme",
    ),
    BrandTheme(
        id="emerald_consulting",
        name="Emerald Consulting",
        primary_color="#064E3B",
        accent_color="#059669",
        background_color="#ECFDF5",
        font_family="Helvetica",
        description="Strategic management consulting and sustainability proposals",
    ),
]


@router.get("", response_model=List[BrandTheme])
async def list_templates():
    """List available enterprise brand themes and styling palettes."""
    return THEMES
