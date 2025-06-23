from app.models.models import Rating, Movie
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.ml_models.ml_models import get_movie_recommendations
from app.services.moviedata import get_movie_data
import pandas as pd

def recommend(user_id: int, db: Session, top_n: int = 10):
    """
    Recommend movies to a user based on their top-rated movies
    Args:
        user_id: The user's ID
        db: Database session
        top_n: Number of top-rated movies to consider
    Returns:
        DataFrame: Recommended movies with scores
    """
    # Get user's top-rated movies from database
    user_ratings = db.query(Rating).filter(Rating.user_id == user_id).order_by(desc(Rating.rating)).limit(top_n).all()
    
    if not user_ratings:
        return pd.DataFrame()  # Return empty DataFrame if no ratings
    
    all_recommendations = []
    
    for rating in user_ratings:
        # Get movie title from database
        movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
        if not movie:
            continue
            
        # Get recommendations for this movie
        recommendations = get_movie_recommendations(movie.title, top_n=5)
        
        if recommendations is not None and not recommendations.empty:
            # Add user's rating as a weight for this movie's recommendations
            recommendations['source_movie'] = movie.title
            recommendations['user_rating'] = rating.rating
            recommendations['weighted_score'] = recommendations['vote_average'] * (rating.rating / 10.0)
            
            all_recommendations.append(recommendations)
    
    if not all_recommendations:
        return pd.DataFrame()
    
    # Combine all recommendations
    combined_recommendations = pd.concat(all_recommendations, ignore_index=True)
    
    # Remove duplicates and aggregate scores
    final_recommendations = combined_recommendations.groupby(['id', 'title', 'vote_average', 'vote_count', 'genre_ids']).agg({
        'source_movie': lambda x: list(x),
        'user_rating': 'mean',
        'weighted_score': 'sum'
    }).reset_index()
    
    # Sort by weighted score (higher is better)
    final_recommendations = final_recommendations.sort_values('weighted_score', ascending=False)
    
    # Remove movies the user has already rated
    user_rated_movie_ids = [rating.movie_id for rating in user_ratings]
    final_recommendations = final_recommendations[~final_recommendations['id'].isin(user_rated_movie_ids)]
    
    return final_recommendations.head(top_n)

def get_user_top_movies(user_id: int, db: Session, top_n: int = 10):
    """
    Get a user's top-rated movies
    Args:
        user_id: The user's ID
        db: Database session
        top_n: Number of top movies to return
    Returns:
        List: User's top-rated movies with ratings
    """
    user_ratings = db.query(Rating, Movie).join(Movie).filter(
        Rating.user_id == user_id
    ).order_by(desc(Rating.rating)).limit(top_n).all()
    
    return [
        {
            'movie_id': rating.movie_id,
            'title': movie.title,
            'rating': rating.rating,
            'genre': movie.genre,
            'director': movie.director,
            'year': movie.year
        }
        for rating, movie in user_ratings
    ] 