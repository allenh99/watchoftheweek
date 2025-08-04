from app.models.models import Rating, Movie
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.ml_models.ml_models import get_movie_recommendations
from app.services.moviedata import get_movie_data
import pandas as pd
import random
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

def recommend(user_id: int, db: Session, top_n: int = 10, sample_from_top_x: int = 100):
    """
    Recommend movies to a user based on a random sample of their top-rated movies
    Args:
        user_id: The user's ID
        db: Database session
        top_n: Number of recommendations to return
        sample_from_top_x: Number of top-rated movies to sample from
    Returns:
        DataFrame: Recommended movies with scores
    """
    user_ratings_all = db.query(Rating).filter(Rating.user_id == user_id).order_by(desc(Rating.rating)).limit(sample_from_top_x).all()
    
    if not user_ratings_all:
        return pd.DataFrame()
    

    if len(user_ratings_all) > top_n:
        user_ratings = random.sample(user_ratings_all, top_n)
    else:
        user_ratings = user_ratings_all
    

    all_user_rated_movies = db.query(Rating.movie_id).filter(Rating.user_id == user_id).all()
    user_rated_movie_ids = [rating.movie_id for rating in all_user_rated_movies]
    
    all_recommendations = []
    
    print("Source movies for recommendations:")
    for rating in user_ratings:
        movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
        if movie:
            print(f"{movie.title} (rating: {rating.rating})")
        if not movie:
            continue
            
        recommendations = get_movie_recommendations(movie.title, top_n=5)
        
        if recommendations is not None and not recommendations.empty:

            recommendations = recommendations[~recommendations['id'].isin(user_rated_movie_ids)]
            
            if not recommendations.empty:
                recommendations['source_movie'] = movie.title
                recommendations['user_rating'] = rating.rating
                recommendations['weighted_score'] = rating.rating
                
                all_recommendations.append(recommendations)
    
    if not all_recommendations:
        return pd.DataFrame()
    
    combined_recommendations = pd.concat(all_recommendations, ignore_index=True)
    
    combined_recommendations['genre_ids_str'] = combined_recommendations['genre_ids'].astype(str)
    
    final_recommendations = combined_recommendations.groupby(['id', 'title', 'vote_average', 'vote_count', 'genre_ids_str', 'poster_path']).agg({
        'source_movie': lambda x: list(x),
        'user_rating': 'mean',
        'weighted_score': 'sum'
    }).reset_index()

    print('DEBUG: source_movie lists for recommendations:')
    print(final_recommendations[['title', 'source_movie']])
    
    final_recommendations['genre_ids'] = final_recommendations['genre_ids_str'].apply(eval)
    final_recommendations = final_recommendations.drop('genre_ids_str', axis=1)
    
    final_recommendations = final_recommendations.sort_values('weighted_score', ascending=False)
    
    print(f"User has rated {len(user_rated_movie_ids)} movies total")
    print(f"Final recommendations: {len(final_recommendations)} (already filtered)")
    
    return final_recommendations.head(top_n)

def cluster_user_movies(user_id: int, db: Session, n_clusters: int = 6):
    """
    Cluster user's rated movies into similar groups and select one representative from each cluster
    Args:
        user_id: The user's ID
        db: Database session
        n_clusters: Number of clusters to create (default 6)
    Returns:
        List: One representative movie from each cluster
    """
    user_ratings = db.query(Rating, Movie).join(Movie).filter(
        Rating.user_id == user_id
    ).order_by(desc(Rating.rating)).all()
    
    if len(user_ratings) < n_clusters:
        print(f"User has only {len(user_ratings)} rated movies, cannot create {n_clusters} clusters")
        return [rating for rating, movie in user_ratings]
    
    movie_features = []
    movie_ratings = []
    
    for rating, movie in user_ratings:
        features = []
        
        features.append(rating.rating / 5.0)
        
        if hasattr(movie, 'year') and movie.year:
            try:
                year_normalized = (movie.year - 1900) / (2024 - 1900)
                features.append(year_normalized)
            except:
                features.append(0.5)
        else:
            features.append(0.5)
        
        features.append(1.0 if hasattr(movie, 'genre') and movie.genre else 0.0)
        
        features.append(1.0 if hasattr(movie, 'director') and movie.director else 0.0)
        
        movie_features.append(features)
        movie_ratings.append(rating)
    
    if len(movie_features) < n_clusters:
        print(f"Only {len(movie_features)} movies have features, cannot create {n_clusters} clusters")
        return [rating for rating in movie_ratings]
    
    X = np.array(movie_features)
    
    effective_clusters = min(n_clusters, len(X))
    if effective_clusters < 2:
        print(f"Not enough data for clustering, returning top {n_clusters} movies")
        return [rating for rating in movie_ratings[:n_clusters]]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=effective_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    selected_ratings = []
    cluster_info = []
    
    for cluster_id in range(kmeans.n_clusters):
        cluster_indices = np.where(cluster_labels == cluster_id)[0]
        if len(cluster_indices) > 0:
            cluster_ratings = [movie_ratings[i] for i in cluster_indices]
            cluster_ratings.sort(key=lambda r: r.rating, reverse=True)
            best_rating = cluster_ratings[0]
            selected_ratings.append(best_rating)
            
            movie = db.query(Movie).filter(Movie.id == best_rating.movie_id).first()
            cluster_size = len(cluster_ratings)
            print(f"Cluster {cluster_id + 1}: {movie.title if movie else best_rating.movie_id} (rating: {best_rating.rating}, size: {cluster_size})")
            
            cluster_info.append({
                'cluster_id': cluster_id + 1,
                'size': cluster_size,
                'movies': [movie_ratings[i] for i in cluster_indices]
            })
    
    return selected_ratings

def recommend_clustered(user_id: int, db: Session, top_n: int = 6, n_clusters: int = 6):
    """
    Recommend movies using clustered source movies - one recommendation per cluster
    Each recommendation comes from a different cluster of similar movies
    Args:
        user_id: The user's ID
        db: Database session
        top_n: Number of recommendations to return (should equal n_clusters)
        n_clusters: Number of clusters to create (default 6, reduced from 12)
    Returns:
        DataFrame: Recommended movies with scores
    """

    source_ratings = cluster_user_movies(user_id, db, n_clusters)
    
    if not source_ratings:
        return pd.DataFrame()
    

    all_user_rated_movies = db.query(Rating.movie_id).filter(Rating.user_id == user_id).all()
    user_rated_movie_ids = [rating.movie_id for rating in all_user_rated_movies]
    
    final_recommendations = []
    
    print(f"Using {len(source_ratings)} clustered source movies:")
    for i, rating in enumerate(source_ratings):
        movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
        if not movie:
            continue
            
        print(f"  Cluster {i+1}: {movie.title} (rating: {rating.rating})")
        

        recommendations = get_movie_recommendations(movie.title, top_n=20)
        
        if recommendations is not None and not recommendations.empty:

            recommendations = recommendations[~recommendations['id'].isin(user_rated_movie_ids)]
            
            if not recommendations.empty:

                best_recommendation = recommendations.iloc[0].copy()
                best_recommendation['source_movie'] = movie.title
                best_recommendation['user_rating'] = rating.rating
                best_recommendation['weighted_score'] = rating.rating
                best_recommendation['cluster_id'] = i + 1
                
                final_recommendations.append(best_recommendation)
                print(f"    → Selected: {best_recommendation['title']}")
    
    if not final_recommendations:
        return pd.DataFrame()
    
    result_df = pd.DataFrame(final_recommendations)
    
    result_df = result_df.sort_values('cluster_id')
    
    print(f"Final recommendations: {len(result_df)} (one per cluster)")
    
    return result_df.head(top_n)

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
    try:
        # First, try to get just the ratings to see if they exist   
        ratings_only = db.query(Rating).filter(Rating.user_id == user_id).all()
        print(f"Found {len(ratings_only)} ratings for user {user_id}")
        
        if not ratings_only:
            print(f"No ratings found for user {user_id}")
            return []
        

        user_ratings = db.query(Rating, Movie).join(Movie).filter(
            Rating.user_id == user_id
        ).order_by(desc(Rating.rating)).limit(top_n).all()
        
        print(f"Query returned {len(user_ratings)} results with movie details")
        
        result = []
        for rating, movie in user_ratings:
            try:
                movie_data = {
                    'movie_id': rating.movie_id,
                    'title': movie.title,
                    'rating': rating.rating,
                    'genre': getattr(movie, 'genre', None),
                    'director': getattr(movie, 'director', None),
                    'year': getattr(movie, 'year', None)
                }
                result.append(movie_data)
            except Exception as e:
                print(f"Error processing movie {movie.id}: {e}")
                # Fallback: just return basic info  
                movie_data = {
                    'movie_id': rating.movie_id,
                    'title': f"Movie ID: {rating.movie_id}",
                    'rating': rating.rating,
                    'genre': None,
                    'director': None,
                    'year': None
                }
                result.append(movie_data)
        
        return result
        
    except Exception as e:
        print(f"Error in get_user_top_movies: {e}")

        try:
            ratings = db.query(Rating).filter(Rating.user_id == user_id).order_by(desc(Rating.rating)).limit(top_n).all()
            return [
                {
                    'movie_id': rating.movie_id,
                    'title': f"Movie ID: {rating.movie_id}",
                    'rating': rating.rating,
                    'genre': None,
                    'director': None,
                    'year': None
                }
                for rating in ratings
            ]
        except Exception as e2:
            print(f"Fallback query also failed: {e2}")
            return [] 