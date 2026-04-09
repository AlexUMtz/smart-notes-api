from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Título de la nota")
    content: str = Field(..., min_length=1, description="Contenido de la nota")


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100, description="Título de la nota")
    content: str | None = Field(default=None, min_length=1, description="Contenido de la nota")    


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    created_at: datetime
    updated_at: datetime | None
    
    model_config = ConfigDict(from_attributes=True)
