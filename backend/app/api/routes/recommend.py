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
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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
