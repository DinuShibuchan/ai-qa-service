from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict

# --- Answer Schemas ---

class AnswerBase(BaseModel):
    text: str

class AnswerCreate(AnswerBase):
    pass

class AnswerResponse(AnswerBase):
    id: int
    question_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# --- Question Schemas ---

class QuestionBase(BaseModel):
    text: str

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    answers: List[AnswerResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# --- Ask Schemas ---

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[str] = []


