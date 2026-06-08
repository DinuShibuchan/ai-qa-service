from fastapi import APIRouter
from app.routes import health, qa, ask, document

api_router = APIRouter()

# Register sub-routers
api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(qa.router, prefix="/qa", tags=["qa"])
api_router.include_router(ask.router, prefix="/ask", tags=["qa"])
api_router.include_router(document.router, prefix="/documents", tags=["documents"])


