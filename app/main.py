from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
# Import all models to ensure they are registered on the Base metadata before tables are created
from app.models.qa import Question, Answer  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.routes.api import api_router
from app.routes.health import router as health_router
from app.routes.ask import router as ask_router
from app.routes.document import router as document_router
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    On startup: Creates all database tables if they do not exist.
    On shutdown: Cleans up the database engine pool.
    """
    # Auto-create tables (useful for development/quickstart)
    # Note: For production environments, Alembic database migrations are highly recommended.
    async with engine.begin() as conn:
        # Enable pgvector extension in Postgres prior to creating tables
        if engine.dialect.name == "postgresql":
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Close connection pool
    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register routes with the configured prefix
app.include_router(api_router, prefix=settings.API_V1_STR)

# Register endpoints at the root level as well
app.include_router(health_router, prefix="/health", tags=["system"])
app.include_router(ask_router, prefix="/ask", tags=["qa"])
app.include_router(document_router, prefix="/documents", tags=["documents"])

@app.get("/")
async def root():
    return {
        "message": f"Welcome to the {settings.APP_NAME}!",
        "docs_url": "/docs",
        "endpoints": {
            "health_check": "/health",
            "ask": "/ask",
            "documents": "/documents",
            "api_v1_prefix": settings.API_V1_STR
        }
    }

