from pydantic import BaseModel

class RatingCreate(BaseModel):
    movie_id: int
    rating: float

class RatingOut(RatingCreate):
    user_id: int
    class Config:
        orm_mode = True
