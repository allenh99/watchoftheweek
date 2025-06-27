from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database import SessionLocal
from app.models.models import Movie, Rating
from app.services import recommender
import pandas as pd

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#takes movies that the user has rated and passes them through recommendation engine
@router.get("/recommendations/{user_id}")
def recommend_movies(user_id: int, db: Session = Depends(get_db), top_n: int = 10):
    try:
        # Get recommendations using the recommender service
        recommendations_df = recommender.recommend(user_id, db, top_n=top_n)
        
        if recommendations_df is None or recommendations_df.empty:
            return {
                "user_id": user_id,
                "message": "No recommendations found. User may not have rated enough movies.",
                "recommendations": []
            }
        
        # Convert DataFrame to list of dictionaries
        recommendations_list = []
        for idx, row in recommendations_df.iterrows():
            recommendations_list.append({
                "movie_id": int(row['id']),
                "title": row['title'],
                "vote_average": float(row['vote_average']),
                "vote_count": int(row['vote_count']),
                "genre_ids": row['genre_ids'],
                "weighted_score": float(row['weighted_score']),
                "source_movies": row['source_movie'],
                "user_rating": float(row['user_rating'])
            })
        
        return {
            "user_id": user_id,
            "recommendations": recommendations_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@router.get("/user-top-movies/{user_id}")
def get_user_top_movies(user_id: int, db: Session = Depends(get_db), top_n: int = 10):
    """Get a user's top-rated movies"""
    try:
        top_movies = recommender.get_user_top_movies(user_id, db, top_n=top_n)
        
        return {
            "user_id": user_id,
            "top_movies": top_movies
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user top movies: {str(e)}")
