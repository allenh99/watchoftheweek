from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import Rating
from app.schemas.schemas import RatingCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ratings")
def create_rating(rating: RatingCreate, db: Session = Depends(get_db)):
    new_rating = Rating(user_id=1, **rating.dict())  # Hardcoded user
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating
