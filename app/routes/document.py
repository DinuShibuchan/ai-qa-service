from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentSearchResponse
from app.services.document_service import DocumentService

router = APIRouter()

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def insert_document(
    schema: DocumentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document. Generates its OpenAI vector embedding, and stores 
    both the text content and embedding in the database.
    """
    try:
        return await DocumentService.insert_document(db, schema)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during insert: {str(e)}"
        )

@router.get("/search", response_model=List[DocumentSearchResponse])
async def search_similar_documents(
    query: str,
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve top-k similar documents based on cosine similarity 
    between document embeddings and the query vector.
    """
    try:
        results = await DocumentService.search_similar_documents(db, query, limit)
        # Map list of tuples (Document, similarity_score) to DocumentSearchResponse schemas
        return [
            DocumentSearchResponse(
                id=doc.id,
                content=doc.content,
                similarity=sim
            )
            for doc, sim in results
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during search: {str(e)}"
        )
