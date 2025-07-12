from pydantic import BaseModel, EmailStr
from typing import Optional

class RatingCreate(BaseModel):
    movie_id: int
    rating: float

class RatingOut(RatingCreate):
    user_id: int
    class Config:
        orm_mode = True

# Authentication schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
