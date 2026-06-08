import json
from sqlalchemy import Text, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db.base import Base

class SafeVector(TypeDecorator):
    """
    A vector type that compiles to pgvector's Vector type on PostgreSQL,
    and falls back to JSON-serialized Text on SQLite/other dialects.
    """
    impl = Text
    cache_ok = True
    
    def __init__(self, dimensions: int):
        super().__init__()
        self.dimensions = dimensions
        
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector(self.dimensions))
        else:
            return dialect.type_descriptor(Text())
            
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        # For SQLite/others, serialize vector list to a JSON string
        return json.dumps(value)
        
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        # For SQLite/others, deserialize JSON string back to a list of floats
        return json.loads(value)

class Document(Base):
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Store OpenAI's standard 1536-dimensional embeddings (works on both pgvector and SQLite)
    embedding: Mapped[list[float]] = mapped_column(SafeVector(1536), nullable=False)

