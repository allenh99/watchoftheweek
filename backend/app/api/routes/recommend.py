from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database import SessionLocal
from app.models.models import Movie, Rating, User
from app.services import recommender
from app.auth import get_current_user
import pandas as pd

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#takes movies that the user has rated and passes them through recommendation engine
@router.get("/recommendations")
def recommend_movies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), top_n: int = 10):
    try:
        # Get recommendations using the recommender service
        recommendations_df = recommender.recommend(current_user.id, db, top_n=top_n)
        
        if recommendations_df is None or recommendations_df.empty:
            return {
                "user_id": current_user.id,
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
                "user_rating": float(row['user_rating']),
                "poster_path": row.get('poster_path', None)
            })
        
        return {
            "user_id": current_user.id,
            "recommendations": recommendations_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@router.get("/user-top-movies/{user_id}")
def get_user_top_movies(user_id: int, db: Session = Depends(get_db), top_n: int = 10):
    """Get a user's top-rated movies"""
    try:
        print(f"API: Getting top movies for user {user_id}")
        
        # First check if user exists and has ratings
        user_ratings_count = db.query(Rating).filter(Rating.user_id == user_id).count()
        print(f"API: User {user_id} has {user_ratings_count} ratings")
        
        if user_ratings_count == 0:
            return {
                "user_id": user_id,
                "message": f"No ratings found for user {user_id}",
                "top_movies": []
            }
        
        top_movies = recommender.get_user_top_movies(user_id, db, top_n=top_n)
        print(f"API: Retrieved {len(top_movies)} top movies")
        
        return {
            "user_id": user_id,
            "top_movies": top_movies
        }
        
    except Exception as e:
        print(f"API Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching user top movies: {str(e)}")
