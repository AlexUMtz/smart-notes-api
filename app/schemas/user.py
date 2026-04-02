from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length= 3, max_length=30, description="Username between 3 and 30 characters")
    password: str = Field(..., min_length= 8, max_length=72, description="Password minimum 8 characters, maximum 72 characters")
    
    model_config = ConfigDict(from_attributes=True)
    
    
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)