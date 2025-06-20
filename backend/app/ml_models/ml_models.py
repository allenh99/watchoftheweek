import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from app.services.moviedata import get_movie_id_by_name

def get_movie_recommendations(movie_name, top_n=10):
    # Load the data
    df = pd.read_csv('app/data/top_popular_movies.csv')
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
    
    # Fit KNN model
    knn = NearestNeighbors(n_neighbors=top_n + 1, algorithm='auto')
    knn.fit(X_scaled)
    
    # Get the movie ID for the input movie
    movie_id = get_movie_id_by_name(movie_name)
    
    if movie_id is None:
        return None
    
    # Find the movie in our dataset
    movie_idx = df[df['id'] == movie_id].index
    if len(movie_idx) == 0:
        print(f"Movie '{movie_name}' not found in the dataset")
        return None
    
    movie_idx = movie_idx[0]
    
    # Get the features for the input movie
    movie_features = X_scaled[movie_idx].reshape(1, -1)
    
    # Get the recommendations
    distances, indices = knn.kneighbors(movie_features)
    
    # Remove the movie itself from recommendations (it's the first neighbor)
    indices = indices[0][1:]  # Skip the first one (the movie itself)
    
    # Get the recommended movies
    recommended_movies = df.iloc[indices][['id', 'title', 'vote_average', 'vote_count', 'genre_ids']]
    
    return recommended_movies
    