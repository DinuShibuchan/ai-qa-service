from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Question(Base):
    __tablename__ = "questions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationship to answers. Use lazy="selectin" to eagerly load related records 
    # and avoid asyncio "MissingGreenlet" errors when reading lazy relationships.
    answers: Mapped[List["Answer"]] = relationship(
        back_populates="question", 
        cascade="all, delete-orphan", 
        lazy="selectin"
    )

class Answer(Base):
    __tablename__ = "answers"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), 
        nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    question: Mapped["Question"] = relationship(back_populates="answers")
