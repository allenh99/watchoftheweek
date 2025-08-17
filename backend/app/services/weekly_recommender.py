from app.models.models import Rating, Movie, User, Recommendation
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.ml_models.ml_models import get_movie_recommendations
from app.services.recommender import cluster_user_movies
from app.services.moviedata import get_movie_data, movie_recommendations
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
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    print(f"Looking for recommendations from: {week_ago}")

    all_recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == user_id
    ).order_by(Recommendation.time_generated.desc()).all()
    print(f"All recommendations for user {user_id}: {len(all_recommendations)}")
    for rec in all_recommendations:
        print(f"  - ID: {rec.id}, Movie: {rec.movie_id}, Time: {rec.time_generated}")
    
    existing_recommendation = db.query(Recommendation).filter(
        Recommendation.user_id == user_id,
        Recommendation.time_generated >= week_ago
    ).order_by(Recommendation.time_generated.desc()).first()
    print("Existing recommendation: ", existing_recommendation)
    
    need_new_recommendation = False
    print("Force new: ", force_new)
    
    if existing_recommendation is None:
        print("No existing recommendation")
        need_new_recommendation = True
    elif force_new:
        print("Force new recommendation")
        need_new_recommendation = True
    else:
        print(f"Last recommendation time: {existing_recommendation.time_generated}")
        print(f"Week ago time: {week_ago}")
        print(f"Time difference: {datetime.utcnow() - existing_recommendation.time_generated}")
        
        if existing_recommendation.time_generated < week_ago:
            print("Week has passed since last recommendation")
            need_new_recommendation = True
        else:
            print("Using existing recommendation - week has not passed")
            need_new_recommendation = False
    print("NEED NEW RECOMMENDATION: ", need_new_recommendation)
    if need_new_recommendation:
        print(f"Generating new recommendation for user {user_id}")
        recommendation = generate_weekly_recommendation(user_id, db)
        
        if recommendation:
            print(f"Generated recommendation: {recommendation}")
            source_movies_str = ",".join(recommendation.get('source_movie', []))
            print(f"Saving recommendation with source_movies: {source_movies_str}")
            new_recommendation = Recommendation(
                user_id=user_id,
                movie_id=recommendation['movie_id'],
                source_movies=source_movies_str,
                time_generated=datetime.utcnow()
            )
            db.add(new_recommendation)
            db.commit()
            print(f"Successfully saved recommendation to database")
            
            print(f"Generated new weekly recommendation for user {user_id}: {recommendation['title']}")
            return recommendation
        else:
            print(f"Failed to generate recommendation for user {user_id}")
            return None
    else:
        movie = db.query(Movie).filter(Movie.id == existing_recommendation.movie_id).first()
        print("Movie: ", movie)
        if movie:
            tmdb_data = get_movie_data(movie.id)
            
            source_movies = []
            if existing_recommendation.source_movies:
                source_movies = [x.strip() for x in existing_recommendation.source_movies.split(',') if x.strip()]
            
            recommendation = {
                'movie_id': movie.id,
                'title': movie.title,
                'genre': movie.genre,
                'director': movie.director,
                'year': movie.year,
                'vote_count': tmdb_data.get('vote_count') if tmdb_data else None,
                'overview': tmdb_data.get('overview') if tmdb_data else None,
                'is_new': False,
                "genre_ids": tmdb_data.get('genre_ids', None),
                "poster_path": tmdb_data.get('poster_path', None),
                "backdrop_path": tmdb_data.get('backdrop_path', None),
                "release_date": tmdb_data.get('release_date', None),
                "overview": tmdb_data.get('overview', None),
                "tagline": tmdb_data.get('tagline', None),
                "director": tmdb_data.get('director', None),
                'source_movie': source_movies,
                'generated_date': existing_recommendation.time_generated.isoformat()
            }
            
            print(f"Returning existing weekly recommendation for user {user_id}: {recommendation['title']}")
            return recommendation
        else:
            print(f"Movie {existing_recommendation.movie_id} not found in database, attempting to recreate...")
            movie_data = get_movie_data(existing_recommendation.movie_id)
            
            if movie_data:
                genre_ids = movie_data.get('genre_ids', [])
                if genre_ids is None:
                    genre_ids = []
                
                release_date = movie_data.get('release_date')
                year = None
                if release_date:
                    if isinstance(release_date, str):
                        year = int(release_date[:4]) if len(release_date) >= 4 else None
                    else:
                        year = release_date.year
                
                movie = Movie(
                    id=movie_data['id'],
                    title=movie_data['title'],
                    genre=", ".join([str(g) for g in genre_ids]),
                    director=movie_data.get('director', 'Unknown'),
                    year=year
                )
                db.add(movie)
                db.commit()
                print(f"Recreated movie: {movie.title} (ID: {movie.id})")
                
                tmdb_data = get_movie_data(movie.id)
                
                source_movies = []
                if existing_recommendation.source_movies:
                    source_movies = [x.strip() for x in existing_recommendation.source_movies.split(',') if x.strip()]
                
                recommendation = {
                    'movie_id': movie.id,
                    'title': movie.title,
                    'genre': movie.genre,
                    'director': movie.director,
                    'year': movie.year,
                    'vote_count': tmdb_data.get('vote_count') if tmdb_data else None,
                    'overview': tmdb_data.get('overview') if tmdb_data else None,
                    'is_new': False,
                    "genre_ids": tmdb_data.get('genre_ids', None),
                    "poster_path": tmdb_data.get('poster_path', None),
                    "backdrop_path": tmdb_data.get('backdrop_path', None),
                    "release_date": tmdb_data.get('release_date', None),
                    "overview": tmdb_data.get('overview', None),
                    "tagline": tmdb_data.get('tagline', None),
                    "director": tmdb_data.get('director', None),
                    'source_movie': source_movies,
                    'generated_date': existing_recommendation.time_generated.isoformat()
                }
                
                print(f"Returning recreated weekly recommendation for user {user_id}: {recommendation['title']}")
                return recommendation
            else:
                print(f"Could not recreate movie {existing_recommendation.movie_id}, generating new recommendation")
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
    
    num_to_select = min(10, len(source_ratings))
    selected_ratings = random.sample(source_ratings, num_to_select)
    #print(selected_ratings)
    
    all_user_rated_movies = db.query(Rating.movie_id).filter(Rating.user_id == user_id).all()
    user_rated_movie_ids = [rating.movie_id for rating in all_user_rated_movies]
    all_recommendations = {}
    #print("All user rated movie ids: ", user_rated_movie_ids)

    for selected_rating in selected_ratings:
        source_movie = db.query(Movie).filter(Movie.id == selected_rating.movie_id).first()
        source_movie_name = source_movie.title if source_movie else f"Movie ID {selected_rating.movie_id}"
        
        recs = movie_recommendations(selected_rating.movie_id)
        for rec in recs:
            if rec['id'] in user_rated_movie_ids:
                continue
            if rec['id'] in all_recommendations:
                all_recommendations[rec['id']].append(source_movie_name)
            else:
                all_recommendations[rec['id']] = [source_movie_name]
    
    selected_recommendation_id = max(all_recommendations, key=lambda x: len(all_recommendations[x]))
    detailed_movie_data = get_movie_data(selected_recommendation_id)
    source_movies = all_recommendations[selected_recommendation_id]
    print(f"Source movies: {source_movies}")
    if detailed_movie_data:
        recommendation = {
            'movie_id': selected_recommendation_id,
            'title': detailed_movie_data['title'],
            'genre_ids': detailed_movie_data.get('genre_ids', []),
            'poster_path': detailed_movie_data.get('poster_path', None),
            'overview': detailed_movie_data.get('overview', None),
            'source_movie': all_recommendations[selected_recommendation_id],
            'backdrop_path': detailed_movie_data.get('backdrop_path', None),
            'release_date': detailed_movie_data.get('release_date', None),
            'tagline': detailed_movie_data.get('tagline', None),
            'director': detailed_movie_data.get('director', None),
            'is_new': True,
            'generated_date': datetime.utcnow().isoformat()
        }
        
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
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    existing_recommendation = db.query(Recommendation).filter(
        Recommendation.user_id == user_id,
        Recommendation.time_generated >= week_ago
    ).order_by(Recommendation.time_generated.desc()).first()
    
    if existing_recommendation is None:
        return {
            'has_recommendation': False,
            'days_until_new': 0,
            'can_generate_new': True,
            'last_generated': None
        }
    
    days_until_new = 0
    if existing_recommendation.time_generated > week_ago:
        time_until_new = existing_recommendation.time_generated + timedelta(days=7) - datetime.utcnow()
        days_until_new = max(0, time_until_new.days)
    
    return {
        'has_recommendation': True,
        'days_until_new': days_until_new,
        'can_generate_new': days_until_new == 0,
        'last_generated': existing_recommendation.time_generated.isoformat()
    } 