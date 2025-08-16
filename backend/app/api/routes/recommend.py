from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database import SessionLocal
from app.models.models import Movie, Rating, User, Recommendation
from app.services import recommender, weekly_recommender, moviedata
from app.auth import get_current_user
import pandas as pd
from datetime import datetime, timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#takes movies that the user has rated and passes them through recommendation engine
@router.get("/recommendations")
def recommend_movies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), top_n: int = 6, use_clustering: bool = True):
    """
    Get movie recommendations for the current user
    Args:
        top_n: Number of recommendations to return (default 6, reduced from 12)
        use_clustering: Whether to use clustering for diverse recommendations (default True)
    """
    try:
        # Get recommendations using the recommender service
        if use_clustering:
            recommendations_df = recommender.recommend_clustered(current_user.id, db, top_n=top_n, n_clusters=top_n)
        else:
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
            # Handle source_movies - it can be a list or a single string
            source_movies = row['source_movie']
            if isinstance(source_movies, list):
                source_movies_list = source_movies
            else:
                source_movies_list = [source_movies] if source_movies else []
            
            recommendations_list.append({
                "movie_id": int(row['id']),
                "title": row['title'],
                #"vote_average": float(row['vote_average']),
                #"vote_count": int(row['vote_count']),
                "genre_ids": row['genre_ids'],
                "weighted_score": float(row['weighted_score']),
                "source_movies": source_movies_list,
                "user_rating": float(row['user_rating']),
                "poster_path": row.get('poster_path', None),
                "cluster_id": int(row.get('cluster_id', 0)),
                "backdrop_path": row.get('backdrop_path', None),
                "release_date": row.get('release_date', None),
                "overview": row.get('overview', None)
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

@router.get("/weekly-recommendation/{user_id}")
def get_weekly_recommendation(user_id: int, db: Session = Depends(get_db), force_new: bool = False):
    """
    Get the user's weekly movie recommendation
    Args:
        user_id: The user's ID
        force_new: Force generation of a new recommendation (ignores weekly cycle)
    """
    try:
        print(f"API: Called with user_id={user_id}, force_new={force_new}")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get recommendation from the weekly recommender service
        # This service handles checking for existing recommendations and saving new ones
        recommendation = weekly_recommender.get_weekly_recommendation(user_id, db, force_new=force_new)
        
        if recommendation is None:
            return {
                "user_id": user_id,
                "message": "No weekly recommendation available. User may not have rated enough movies.",
                "recommendation": None
            }
        
        return {
            "user_id": user_id,
            "recommendation": recommendation,
            "streaming_data": moviedata.get_movie_streaming_data(recommendation['movie_id'])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weekly recommendation: {str(e)}")

@router.get("/weekly-recommendation-status/{user_id}")
def get_weekly_recommendation_status(user_id: int, db: Session = Depends(get_db)):
    """
    Get the status of the user's weekly recommendation
    """
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check for existing weekly recommendation from the last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        existing_recommendation = db.query(Recommendation).filter(
            Recommendation.user_id == user_id,
            Recommendation.time_generated >= week_ago
        ).order_by(Recommendation.time_generated.desc()).first()
        
        if existing_recommendation:
            days_until_new = 7 - (datetime.utcnow() - existing_recommendation.time_generated).days
            return {
                "user_id": user_id,
                "status": {
                    "has_recommendation": True,
                    "last_generated": existing_recommendation.time_generated.isoformat(),
                    "days_until_new": max(0, days_until_new),
                    "can_generate_new": days_until_new <= 0
                }
            }
        else:
            return {
                "user_id": user_id,
                "status": {
                    "has_recommendation": False,
                    "last_generated": None,
                    "days_until_new": 0,
                    "can_generate_new": True
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weekly recommendation status: {str(e)}")
