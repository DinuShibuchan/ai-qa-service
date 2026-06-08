from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.qa import QuestionCreate, QuestionResponse, AnswerCreate, AnswerResponse
from app.services.qa_service import QAService

router = APIRouter()

@router.post("", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    schema: QuestionCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a new question.
    """
    return await QAService.create_question(db, schema)

@router.get("", response_model=List[QuestionResponse])
async def list_questions(
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve questions list (paginated, sorted by ID descending).
    """
    return await QAService.get_questions(db, skip=skip, limit=limit)

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a single question by ID.
    """
    question = await QAService.get_question(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Question not found"
        )
    return question

@router.post("/{question_id}/answers", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def create_answer(
    question_id: int, 
    schema: AnswerCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Answer a specific question.
    """
    answer = await QAService.create_answer(db, question_id, schema)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Question not found"
        )
    return answer
