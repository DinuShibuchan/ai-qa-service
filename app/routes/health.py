from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter()

@router.get("", status_code=200)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Simple health check verifying application and database connectivity.
    """
    try:
        # Run a simple query to verify database is reachable
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )
