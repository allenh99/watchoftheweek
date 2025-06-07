from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database import SessionLocal
from app.models.models import Movie, Rating

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#takes movies that the user has rated and passes them through recommendation engine
@router.get("/recommendations/{user_id}")
def recommend_movies(user_id: int, db: Session = Depends(get_db), limit: int = 5):
    rated_movie_ids = db.query(Rating.movie_id).filter(Rating.user_id == user_id).subquery()
    recommendations = ()

    return {
        "user_id": user_id,
        "recommendations": [
            {"movie_id": movie.id, "title": movie.title, "avg_rating": movie.avg_rating}
            for movie in recommendations
        ]
    }
