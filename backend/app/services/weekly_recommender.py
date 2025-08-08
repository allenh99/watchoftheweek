from app.models.models import Rating, Movie, User
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.ml_models.ml_models import get_movie_recommendations
from app.services.recommender import cluster_user_movies
from app.services.moviedata import get_movie_data
import pandas as pd
import random
from datetime import datetime, timedelta, timezone

def ensure_timezone_aware(dt):
    """Ensure a datetime is timezone-aware, assuming UTC if it's naive"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def get_weekly_recommendation(user_id: int, db: Session, force_new: bool = False):
    """
    Get or generate a weekly recommendation for a user
    Args:
        user_id: The user's ID
        db: Database session
        force_new: Force generation of a new recommendation (ignores weekly cycle)
    Returns:
        dict: Weekly recommendation with movie details
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Check if we need a new recommendation
    need_new_recommendation = False
    
    if user.weekly_recommendation_id is None:
        need_new_recommendation = True
    elif user.weekly_recommendation_date is None:
        need_new_recommendation = True
    elif force_new:
        need_new_recommendation = True
    else:
        # Check if a week has passed since the last recommendation
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        user_date = ensure_timezone_aware(user.weekly_recommendation_date)
        if user_date and user_date < week_ago:
            need_new_recommendation = True
    
    if need_new_recommendation:
        # Generate new weekly recommendation
        recommendation = generate_weekly_recommendation(user_id, db)
        
        if recommendation:
            # Update user with new recommendation
            user.weekly_recommendation_id = recommendation['movie_id']
            user.weekly_recommendation_date = datetime.now(timezone.utc)
            db.commit()
            
            print(f"Generated new weekly recommendation for user {user_id}: {recommendation['title']}")
            return recommendation
        else:
            return None
    else:
        # Return existing recommendation
        movie = db.query(Movie).filter(Movie.id == user.weekly_recommendation_id).first()
        if movie:
            # Get additional movie data from TMDB if available
            tmdb_data = get_movie_data(movie.id)
            
            recommendation = {
                'movie_id': movie.id,
                'title': movie.title,
                'genre': movie.genre,
                'director': movie.director,
                'year': movie.year,
                # 'poster_path': tmdb_data.get('poster_path') if tmdb_data else None,
                # 'vote_average': tmdb_data.get('vote_average') if tmdb_data else None,
                'vote_count': tmdb_data.get('vote_count') if tmdb_data else None,
                'overview': tmdb_data.get('overview') if tmdb_data else None,
                'is_new': False,
                "genre_ids": movie.genre,
                "poster_path": tmdb_data.get('poster_path', None),
                "backdrop_path": tmdb_data.get('backdrop_path', None),
                "release_date": tmdb_data.get('release_date', None),
                "overview": tmdb_data.get('overview', None),
                "tagline": tmdb_data.get('tagline', None),
                "director": tmdb_data.get('director', None),
                'generated_date': ensure_timezone_aware(user.weekly_recommendation_date).isoformat() if user.weekly_recommendation_date else None
            }
            
            print(f"Returning existing weekly recommendation for user {user_id}: {recommendation['title']}")
            return recommendation
        else:
            # Movie was deleted, generate new recommendation
            return get_weekly_recommendation(user_id, db, force_new=True)

def generate_weekly_recommendation(user_id: int, db: Session):
    """
    Generate a new weekly recommendation using clustering
    Args:
        user_id: The user's ID
        db: Database session
    Returns:
        dict: New weekly recommendation
    """
    #source_ratings = cluster_user_movies(user_id, db, n_clusters=1)
    source_ratings = db.query(Rating).filter(Rating.user_id == user_id).filter(Rating.rating >= 4.0).all()
    if not source_ratings:
        return None
    
    all_user_rated_movies = db.query(Rating.movie_id).filter(Rating.user_id == user_id).all()
    user_rated_movie_ids = [rating.movie_id for rating in all_user_rated_movies]
    
    selected_movie = source_ratings[random.randint(0, len(source_ratings) - 1)]
    movie = db.query(Movie).filter(Movie.id == selected_movie.movie_id).first()
    
    if not movie:
        return None
    
    print(f"Generating weekly recommendation from: {movie.title} (rating: {selected_movie.rating})")
    
    recommendations = get_movie_recommendations(movie.title, top_n=50)
    
    if recommendations is not None and not recommendations.empty:
        recommendations = recommendations[~recommendations['id'].isin(user_rated_movie_ids)]
        
        if not recommendations.empty:
            best_recommendation = recommendations.iloc[0]
            print(best_recommendation)
            recommendation = {
                'movie_id': int(best_recommendation['id']),
                'title': best_recommendation['title'],
                'genre_ids': best_recommendation['genre_ids'],
                'poster_path': best_recommendation.get('poster_path', None),
                'overview': best_recommendation.get('overview', None),
                'source_movie': movie.title,
                'user_rating': selected_movie.rating,
                'backdrop_path': best_recommendation.get('backdrop_path', None),
                'release_date': best_recommendation.get('release_date', None),
                'tagline': best_recommendation.get('tagline', None),
                'director': best_recommendation.get('director', None),
                'is_new': True,
                'generated_date': datetime.now(timezone.utc).isoformat()
            }
            
            print(f"Selected weekly recommendation: {recommendation['title']}")
            return recommendation
    
    return None

def get_weekly_recommendation_status(user_id: int, db: Session):
    """
    Get the status of a user's weekly recommendation
    Args:
        user_id: The user's ID
        db: Database session
    Returns:
        dict: Status information about the weekly recommendation
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    if user.weekly_recommendation_id is None or user.weekly_recommendation_date is None:
        return {
            'has_recommendation': False,
            'days_until_new': 0,
            'can_generate_new': True
        }
    
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    days_until_new = 0
    
    user_date = ensure_timezone_aware(user.weekly_recommendation_date)
    if user_date and user_date > week_ago:
        time_until_new = user_date + timedelta(days=7) - datetime.now(timezone.utc)
        days_until_new = max(0, time_until_new.days)
    
    return {
        'has_recommendation': True,
        'days_until_new': days_until_new,
        'can_generate_new': days_until_new == 0,
        'last_generated': ensure_timezone_aware(user.weekly_recommendation_date).isoformat() if user.weekly_recommendation_date else None
    } 