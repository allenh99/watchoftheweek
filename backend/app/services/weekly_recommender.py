from app.models.models import Rating, Movie, User
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.ml_models.ml_models import get_movie_recommendations
from app.services.recommender import cluster_user_movies
import pandas as pd
from datetime import datetime, timedelta

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
        week_ago = datetime.utcnow() - timedelta(days=7)
        if user.weekly_recommendation_date < week_ago:
            need_new_recommendation = True
    
    if need_new_recommendation:
        # Generate new weekly recommendation
        recommendation = generate_weekly_recommendation(user_id, db)
        
        if recommendation:
            # Update user with new recommendation
            user.weekly_recommendation_id = recommendation['movie_id']
            user.weekly_recommendation_date = datetime.utcnow()
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
            from app.services.moviedata import get_movie_data
            tmdb_data = get_movie_data(movie.id)
            
            recommendation = {
                'movie_id': movie.id,
                'title': movie.title,
                'genre': movie.genre,
                'director': movie.director,
                'year': movie.year,
                'poster_path': tmdb_data.get('poster_path') if tmdb_data else None,
                'vote_average': tmdb_data.get('vote_average') if tmdb_data else None,
                'vote_count': tmdb_data.get('vote_count') if tmdb_data else None,
                'overview': tmdb_data.get('overview') if tmdb_data else None,
                'is_new': False,
                'generated_date': user.weekly_recommendation_date.isoformat() if user.weekly_recommendation_date else None
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
    # Get clustered source movies (use 1 cluster for weekly recommendation)
    source_ratings = cluster_user_movies(user_id, db, n_clusters=1)
    
    if not source_ratings:
        return None
    
    # Get ALL movies the user has rated (for filtering)
    all_user_rated_movies = db.query(Rating.movie_id).filter(Rating.user_id == user_id).all()
    user_rated_movie_ids = [rating.movie_id for rating in all_user_rated_movies]
    
    # Get recommendations from the best source movie
    best_rating = source_ratings[0]  # Only one cluster
    movie = db.query(Movie).filter(Movie.id == best_rating.movie_id).first()
    
    if not movie:
        return None
    
    print(f"Generating weekly recommendation from: {movie.title} (rating: {best_rating.rating})")
    
    # Get recommendations for this movie
    recommendations = get_movie_recommendations(movie.title, top_n=50)
    
    if recommendations is not None and not recommendations.empty:
        # Filter out movies the user has already rated
        recommendations = recommendations[~recommendations['id'].isin(user_rated_movie_ids)]
        
        if not recommendations.empty:
            # Select the best recommendation
            best_recommendation = recommendations.iloc[0]
            
            recommendation = {
                'movie_id': int(best_recommendation['id']),
                'title': best_recommendation['title'],
                'vote_average': float(best_recommendation['vote_average']),
                'vote_count': int(best_recommendation['vote_count']),
                'genre_ids': best_recommendation['genre_ids'],
                'poster_path': best_recommendation.get('poster_path'),
                'overview': best_recommendation.get('overview'),
                'source_movie': movie.title,
                'user_rating': best_rating.rating,
                'is_new': True,
                'generated_date': datetime.utcnow().isoformat()
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
    
    # Calculate days until new recommendation
    week_ago = datetime.utcnow() - timedelta(days=7)
    days_until_new = 0
    
    if user.weekly_recommendation_date > week_ago:
        # Calculate remaining days
        time_until_new = user.weekly_recommendation_date + timedelta(days=7) - datetime.utcnow()
        days_until_new = max(0, time_until_new.days)
    
    return {
        'has_recommendation': True,
        'days_until_new': days_until_new,
        'can_generate_new': days_until_new == 0,
        'last_generated': user.weekly_recommendation_date.isoformat() if user.weekly_recommendation_date else None
    } 