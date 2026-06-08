from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.qa import AskRequest, AskResponse
from app.services.qa_service import QAService

router = APIRouter()

@router.post("", response_model=AskResponse, status_code=status.HTTP_201_CREATED)
async def ask_question(
    schema: AskRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Accepts a question, generates a mock response, saves them, and returns the QA payload.
    Includes validation handling for blank or empty inputs and internal database errors.
    """
    try:
        return await QAService.ask_question(db, schema)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Catch-all internal error handler
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected server error occurred: {str(e)}"
        )
