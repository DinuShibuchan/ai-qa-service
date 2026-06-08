from typing import List, Tuple
from sqlalchemy import select, literal
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI
from app.core.config import settings
from app.models.document import Document
from app.schemas.document import DocumentCreate

# Initialize AsyncOpenAI client
openai_client = None
if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip() and settings.OPENAI_API_KEY != "your-openai-api-key-here":
    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class DocumentService:
    @staticmethod
    async def get_embedding(text: str) -> List[float]:
        """
        Queries the OpenAI API to generate a vector embedding for the given text
        using the text-embedding-3-small model.
        Falls back to generating a mock unit vector if the API fails (e.g., quota exceeded).
        """
        if not openai_client:
            # Generate a mock vector if key is not set
            import random
            import math
            print("[WARNING] OpenAI API Key is not configured. Generating a mock 1536-dim vector for testing.")
            vec = [random.uniform(-1.0, 1.0) for _ in range(1536)]
            norm = math.sqrt(sum(x * x for x in vec))
            return [x / norm for x in vec]
        
        try:
            response = await openai_client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            import random
            import math
            print(f"[WARNING] OpenAI Embeddings API failed: {str(e)}. Generating a mock 1536-dim vector for testing.")
            vec = [random.uniform(-1.0, 1.0) for _ in range(1536)]
            norm = math.sqrt(sum(x * x for x in vec))
            return [x / norm for x in vec]


    @staticmethod
    async def insert_document(db: AsyncSession, schema: DocumentCreate) -> Document:
        """
        Generates the vector embedding for the content, then stores
        both the text and its embedding vector inside PostgreSQL.
        """
        content_text = schema.content.strip()
        if not content_text:
            raise ValueError("Document content cannot be empty or blank.")
        
        # Generate the embedding
        embedding = await DocumentService.get_embedding(content_text)
        
        # Insert into the database
        db_doc = Document(content=content_text, embedding=embedding)
        db.add(db_doc)
        await db.commit()
        await db.refresh(db_doc)
        return db_doc

    @staticmethod
    async def search_similar_documents(
        db: AsyncSession, 
        query: str, 
        limit: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Generates a query vector, runs a cosine similarity query against the 
        database using pgvector (or falls back to Python-based cosine calculations on SQLite),
        and returns documents alongside their similarity score.
        Similarity = 1 - Cosine Distance
        """
        query_text = query.strip()
        if not query_text:
            raise ValueError("Search query cannot be empty or blank.")
            
        # Get query embedding vector
        query_embedding = await DocumentService.get_embedding(query_text)
        
        # Determine database dialect
        try:
            dialect_name = db.bind.dialect.name
        except Exception:
            dialect_name = "postgresql"

        if dialect_name == "sqlite":
            # SQLite does not support pgvector. Fetch documents and compute similarity in Python.
            stmt = select(Document)
            result = await db.execute(stmt)
            all_docs = result.scalars().all()
            
            import math
            def cosine_similarity(v1: List[float], v2: List[float]) -> float:
                dot_product = sum(x * y for x, y in zip(v1, v2))
                norm_v1 = math.sqrt(sum(x * x for x in v1))
                norm_v2 = math.sqrt(sum(x * x for x in v2))
                if norm_v1 == 0 or norm_v2 == 0:
                    return 0.0
                return dot_product / (norm_v1 * norm_v2)
            
            scored_docs = []
            for doc in all_docs:
                sim = cosine_similarity(doc.embedding, query_embedding)
                scored_docs.append((doc, sim))
            
            # Sort by similarity score descending
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return scored_docs[:limit]
        
        else:
            # PostgreSQL: use pgvector database distance calculations
            cosine_distance_expr = Document.embedding.cosine_distance(query_embedding)
            
            stmt = select(
                Document,
                (literal(1.0) - cosine_distance_expr).label("similarity")
            ).order_by(
                cosine_distance_expr
            ).limit(limit)
            
            result = await db.execute(stmt)
            return [(row[0], float(row[1])) for row in result.all()]

