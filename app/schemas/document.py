from pydantic import BaseModel, ConfigDict

class DocumentCreate(BaseModel):
    content: str

class DocumentResponse(BaseModel):
    id: int
    content: str
    
    model_config = ConfigDict(from_attributes=True)

class DocumentSearchResponse(BaseModel):
    id: int
    content: str
    similarity: float
    
    model_config = ConfigDict(from_attributes=True)
