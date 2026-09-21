from fastapi import APIRouter
from app.api.v1.proposals import router as proposals_router
from app.api.v1.export import router as export_router
from app.api.v1.templates import router as templates_router

api_router = APIRouter(prefix="/api/v1")

# Mount endpoints
api_router.include_router(proposals_router)
api_router.include_router(export_router)
api_router.include_router(templates_router)
