import asyncio
import sys
import os

# Adjust python path to include the project root so we can import 'app' modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import async_session_local, engine
from app.db.base import Base
from app.models.qa import Question, Answer  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.schemas.document import DocumentCreate
from app.services.document_service import DocumentService
from app.core.config import settings
from sqlalchemy import text

# Sample QA & Tech documents to seed
SAMPLE_DOCUMENTS = [
    "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.",
    "pgvector is an open-source vector similarity search extension for PostgreSQL. It supports L2 distance, inner product, and cosine similarity.",
    "Retrieval-Augmented Generation (RAG) is a technique that combines vector search retrieval with LLM completion APIs to generate factual, context-aware answers.",
    "OpenAI embeddings (such as text-embedding-3-small) translate text segments into high-dimensional numerical vectors that represent semantic meaning.",
    "SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives developers the full power and flexibility of SQL, supporting async drivers.",
    "Pydantic is a data validation and settings management library using Python type annotations. It enforces type hints at runtime with helpful error messages.",
    "Uvicorn is an ASGI web server implementation for Python, commonly used to serve high-performance async frameworks like FastAPI and Starlette."
]

async def seed_data():
    print("Starting database seeding...")
    print(f"Target DB: {settings.DATABASE_URL.split('@')[-1]}") # Print server name only for security
    print(f"OpenAI Model: {settings.OPENAI_MODEL}")
    
    # Verify OpenAI API key is set
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key-here":
        print("\n[ERROR] OpenAI API Key is not configured.")
        print("Please configure OPENAI_API_KEY in your .env file before running this script.")
        sys.exit(1)
        
    # Ensure database tables exist
    print("Initializing database tables...")
    async with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables initialized successfully.")
        
    async with async_session_local() as db:

        for text in SAMPLE_DOCUMENTS:
            print(f"\nProcessing document: '{text[:50]}...'")
            try:
                schema = DocumentCreate(content=text)
                # This automatically calls OpenAI embeddings and saves the document
                doc = await DocumentService.insert_document(db, schema)
                print(f"--> Successfully seeded Document ID {doc.id}")
            except Exception as e:
                print(f"--> [ERROR] Failed to seed document: {str(e)}")
                
    print("\nDatabase seeding completed!")

if __name__ == "__main__":
    # Run the async main loop
    asyncio.run(seed_data())
