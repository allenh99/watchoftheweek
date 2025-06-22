import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.moviedata import get_movie_id_by_name,get_movie_data

def get_movie_recommendations(movie_name, top_n=10):
    # Load the data
    df = pd.read_csv('app/data/top_rated_movies.csv')
    df.dropna(inplace=True)
    
    # Convert genre_ids from string to list and create genre features
    df['genre_ids'] = df['genre_ids'].apply(eval)  # Convert string representation to list
    
    # Create genre features (one-hot encoding for common genres)
    all_genres = set()
    for genres in df['genre_ids']:
        all_genres.update(genres)
    
    # Create binary columns for each genre
    for genre in all_genres:
        df[f'genre_{genre}'] = df['genre_ids'].apply(lambda x: 1 if genre in x else 0)
    
    # Select features for KNN
    feature_columns = ['vote_average', 'vote_count'] + [f'genre_{genre}' for genre in all_genres]
    
    # Prepare features
    X = df[feature_columns].values
    
    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Get the movie ID for the input movie
    movie_id = get_movie_id_by_name(movie_name)
    
    if movie_id is None:
        print(f"Movie '{movie_name}' not found in TMDB")
        return None
    
    # Check if movie is in our dataset
    movie_in_dataset = df[df['id'] == movie_id]
    
    if len(movie_in_dataset) == 0:
        # Movie not in dataset, fetch it from TMDB
        print(f"Movie '{movie_name}' not in dataset, fetching from TMDB...")
        movie_data = get_movie_data(movie_id)
        
        if movie_data is None:
            print(f"Could not fetch data for '{movie_name}'")
            return None
        
        # Create a temporary dataframe with the new movie
        temp_df = pd.DataFrame([movie_data])
        temp_df['genre_ids'] = temp_df['genre_ids'].apply(lambda x: x if isinstance(x, list) else [])
        
        # Add genre features for the new movie
        for genre in all_genres:
            temp_df[f'genre_{genre}'] = temp_df['genre_ids'].apply(lambda x: 1 if genre in x else 0)
        
        # Get features for the new movie
        movie_features = temp_df[feature_columns].values
        
        # Scale the features
        movie_features_scaled = scaler.transform(movie_features)
        
        # Fit KNN model on existing data
        knn = NearestNeighbors(n_neighbors=top_n, algorithm='auto')
        knn.fit(X_scaled)
        
        # Get recommendations
        distances, indices = knn.kneighbors(movie_features_scaled)
        
    else:
        # Movie is in dataset
        movie_idx = movie_in_dataset.index[0]
        
        # Get the features for the input movie
        movie_features = X_scaled[movie_idx].reshape(1, -1)
        
        # Fit KNN model
        knn = NearestNeighbors(n_neighbors=top_n + 1, algorithm='auto')
        knn.fit(X_scaled)
        
        # Get the recommendations
        distances, indices = knn.kneighbors(movie_features)
        
        # Remove the movie itself from recommendations (it's the first neighbor)
        indices = indices[0][1:]  # Skip the first one (the movie itself)
    
    # Get the recommended movies
    if len(indices) > 0:
        # Handle both cases: movie in dataset (indices is 2D) vs not in dataset (indices is 1D)
        if len(indices.shape) > 1:
            indices = indices[0]  # Flatten if 2D array
        
        recommended_movies = df.iloc[indices][['id', 'title', 'vote_average', 'vote_count', 'genre_ids']]
        return recommended_movies
    else:
        print("No recommendations found")
        return None

#res = get_movie_recommendations("The Dark Knight")
#res = get_movie_recommendations("Society of the Snow")
#print(res.head())
    