from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import Rating
from app.schemas.schemas import RatingCreate
from app.services.moviedata import get_movie_id_by_name
from typing import List
import pandas as pd
import io

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#
@router.post("/ratings")
def create_rating(rating: RatingCreate, db: Session = Depends(get_db)):
    new_rating = Rating(user_id=1, **rating.dict())  # Hardcoded user
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

@router.get("/ratings", response_model=List[RatingCreate])
def get_ratings(db: Session = Depends(get_db)):
    ratings = db.query(Rating).all()
    return ratings


@router.post("/ratings/upload")
async def upload_ratings(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Read file into pandas DataFrame
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))


    #TODO: Add movies to database if they don't exist

    for _, row in df.iterrows():
        movie_id = get_movie_id_by_name(row["Name"])
        rating = Rating(
            user_id=user_id,
            movie_id=movie_id,
            rating=row["Rating"]
        )
        db.add(rating)
    db.commit()

    return {"message": f"Uploaded {len(df)} ratings for user {user_id}"}