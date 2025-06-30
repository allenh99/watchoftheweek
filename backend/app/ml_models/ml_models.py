import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import sys
import os
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.moviedata import get_movie_id_by_name,get_movie_data

# Global variables to store the trained model and data
_knn_model = None
_scaler = None
_feature_columns = None
_movie_data = None

def train_and_save_model(csv_file='app/data/top_rated_movies.csv', model_file='app/ml_models/recommender_model.pkl'):
    """
    Train the recommendation model and save it to disk
    """
    global _knn_model, _scaler, _feature_columns, _movie_data
    
    print("Training recommendation model...")
    
    # Load the data
    df = pd.read_csv(csv_file)
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
    knn = NearestNeighbors(n_neighbors=20, algorithm='auto')
    knn.fit(X_scaled)
    
    # Save the model and data
    model_data = {
        'knn_model': knn,
        'scaler': scaler,
        'feature_columns': feature_columns,
        'movie_data': df,
        'all_genres': list(all_genres)
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(model_file), exist_ok=True)
    
    with open(model_file, 'wb') as f:
        pickle.dump(model_data, f)
    
    # Update global variables
    _knn_model = knn
    _scaler = scaler
    _feature_columns = feature_columns
    _movie_data = df
    
    print(f"Model saved to {model_file}")
    return model_data

def load_model(model_file='app/ml_models/recommender_model.pkl'):
    """
    Load the trained model from disk
    """
    global _knn_model, _scaler, _feature_columns, _movie_data
    
    if os.path.exists(model_file):
        print("Loading trained model...")
        with open(model_file, 'rb') as f:
            model_data = pickle.load(f)
        
        _knn_model = model_data['knn_model']
        _scaler = model_data['scaler']
        _feature_columns = model_data['feature_columns']
        _movie_data = model_data['movie_data']
        
        print("Model loaded successfully!")
        return model_data
    else:
        print("No saved model found. Training new model...")
        return train_and_save_model()

def get_movie_recommendations(movie_name, top_n=10):
    """
    Get movie recommendations using the trained model
    """
    global _knn_model, _scaler, _feature_columns, _movie_data
    
    # Load model if not already loaded
    if _knn_model is None:
        load_model()
    
    # Get the movie ID for the input movie
    movie_id = get_movie_id_by_name(movie_name)
    
    if movie_id is None:
        print(f"Movie '{movie_name}' not found in TMDB")
        return None
    
    # Check if movie is in our dataset
    movie_in_dataset = _movie_data[_movie_data['id'] == movie_id]
    
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
        all_genres = set()
        for genres in _movie_data['genre_ids']:
            all_genres.update(genres)
        
        for genre in all_genres:
            temp_df[f'genre_{genre}'] = temp_df['genre_ids'].apply(lambda x: 1 if genre in x else 0)
        
        # Get features for the new movie
        movie_features = temp_df[_feature_columns].values
        
        # Scale the features
        movie_features_scaled = _scaler.transform(movie_features)
        
        # Get recommendations
        distances, indices = _knn_model.kneighbors(movie_features_scaled)
        
        # Handle indices - it's a 2D array, we want the first row
        indices = indices[0]
        
    else:
        # Movie is in dataset
        movie_idx = movie_in_dataset.index[0]
        
        # Get the features for the input movie
        movie_features = _movie_data.iloc[movie_idx][_feature_columns].values.reshape(1, -1)
        
        # Scale the features
        movie_features_scaled = _scaler.transform(movie_features)
        
        # Get the recommendations
        distances, indices = _knn_model.kneighbors(movie_features_scaled)
        
        # Handle indices - it's a 2D array, we want the first row
        indices = indices[0]
        
        # Remove the movie itself from recommendations (it's the first neighbor)
        indices = indices[1:]  # Skip the first one (the movie itself)
    
    # Check if we have any recommendations
    if len(indices) == 0:
        print("No recommendations found")
        return None
    
    # Get the recommended movies
    try:
        recommended_movies = _movie_data.iloc[indices][['id', 'title', 'vote_average', 'vote_count', 'genre_ids']]
        return recommended_movies
    except Exception as e:
        print(f"Error getting recommended movies: {e}")
        return None

# Initialize model on import
try:
    load_model()
except Exception as e:
    print(f"Could not load model: {e}")
    print("Model will be trained on first use.")

#res = get_movie_recommendations("The Dark Knight")
#res = get_movie_recommendations("Society of the Snow")
#print(res.head())
    