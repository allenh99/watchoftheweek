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
    
    print(f"Initial dataset shape: {df.shape}")
    print(f"Initial columns: {df.columns.tolist()}")
    
    # Check if required columns exist
    required_columns = ['id', 'title', 'genre_ids', 'vote_average', 'vote_count', 'original_language']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing required columns in dataset: {missing_columns}")
        return None
    
    # Handle missing data for new features gracefully
    if 'cast' not in df.columns:
        df['cast'] = df.apply(lambda x: [], axis=1)
    if 'director' not in df.columns:
        df['director'] = None
    
    print(f"Before dropna: {len(df)} rows")
    
    # Check for NaN values in each column
    for col in ['id', 'title', 'genre_ids', 'vote_average', 'vote_count']:
        nan_count = df[col].isna().sum()
        print(f"NaN values in {col}: {nan_count}")
    
    # Only drop rows with NaN in critical columns, but be more lenient
    df.dropna(subset=['id', 'title', 'vote_average', 'vote_count'], inplace=True)
    print(f"After dropna: {len(df)} rows")
    
    # Check if we have any data left
    if len(df) == 0:
        print("Error: No valid data remaining after cleaning. Please check your dataset.")
        return None
    
    # Convert genre_ids from string to list and create genre features
    # Handle empty genre_ids gracefully
    df['genre_ids'] = df['genre_ids'].apply(lambda x: eval(x) if pd.notna(x) and x.strip() else [])
    
    # Create genre features (one-hot encoding for common genres)
    all_genres = set()
    for genres in df['genre_ids']:
        all_genres.update(genres)
    
    # Create binary columns for each genre
    for genre in all_genres:
        df[f'genre_{genre}'] = df['genre_ids'].apply(lambda x: 1 if genre in x else 0)
    
    # Handle original language (one-hot encoding for common languages)
    all_languages = set()
    for lang in df['original_language']:
        if pd.notna(lang):
            all_languages.add(lang)
    
    # Create binary columns for each language
    for lang in all_languages:
        df[f'lang_{lang}'] = df['original_language'].apply(lambda x: 1 if x == lang else 0)
    
    # Handle cast members (one-hot encoding for top cast)
    all_cast = set()
    for cast_list in df['cast']:
        if isinstance(cast_list, list):
            all_cast.update(cast_list[:3])  # Top 3 cast members
        elif isinstance(cast_list, str):
            # Handle string representation of cast list
            try:
                cast_eval = eval(cast_list)
                if isinstance(cast_eval, list):
                    all_cast.update(cast_eval[:3])
            except:
                pass
    
    # Create binary columns for each cast member
    for cast_member in all_cast:
        df[f'cast_{cast_member.replace(" ", "_").replace(".", "_")}'] = df['cast'].apply(
            lambda x: 1 if (isinstance(x, list) and cast_member in x) or 
                       (isinstance(x, str) and cast_member in eval(x) if x else False) else 0
        )
    
    # Handle directors (one-hot encoding for directors)
    all_directors = set()
    for director in df['director']:
        if pd.notna(director):
            all_directors.add(director)
    
    # Create binary columns for each director
    for director in all_directors:
        df[f'director_{director.replace(" ", "_").replace(".", "_")}'] = df['director'].apply(
            lambda x: 1 if x == director else 0
        )
    
    # Select features for KNN (pure content-based)
    feature_columns = [f'genre_{genre}' for genre in all_genres] + \
                     [f'lang_{lang}' for lang in all_languages] + \
                     [f'cast_{cast_member.replace(" ", "_").replace(".", "_")}' for cast_member in all_cast] + \
                     [f'director_{director.replace(" ", "_").replace(".", "_")}' for director in all_directors]
    
    # Prepare features
    X = df[feature_columns].values
    
    # Check if we have data to scale
    if len(X) == 0:
        print("Error: No data available for training. Please check your dataset.")
        return None
    
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
        'all_genres': list(all_genres),
        'all_languages': list(all_languages),
        'all_cast': list(all_cast),
        'all_directors': list(all_directors)
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
        
        # Add language features for the new movie
        all_languages = set()
        for lang in _movie_data['original_language']:
            if pd.notna(lang):
                all_languages.add(lang)
        
        for lang in all_languages:
            temp_df[f'lang_{lang}'] = temp_df['original_language'].apply(lambda x: 1 if x == lang else 0)
        
        # Add cast features for the new movie
        all_cast = set()
        for cast_list in _movie_data['cast']:
            if isinstance(cast_list, list):
                all_cast.update(cast_list[:3])
        
        for cast_member in all_cast:
            temp_df[f'cast_{cast_member.replace(" ", "_").replace(".", "_")}'] = temp_df['cast'].apply(
                lambda x: 1 if isinstance(x, list) and cast_member in x else 0
            )
        
        # Add director features for the new movie
        all_directors = set()
        for director in _movie_data['director']:
            if pd.notna(director):
                all_directors.add(director)
        
        for director in all_directors:
            temp_df[f'director_{director.replace(" ", "_").replace(".", "_")}'] = temp_df['director'].apply(
                lambda x: 1 if x == director else 0
            )
        
        # Get features for the new movie
        try:
            movie_features = temp_df[_feature_columns].values
            
            # Check if we have valid features
            if len(movie_features) == 0 or movie_features.shape[1] == 0:
                print(f"Error: No valid features found for '{movie_name}'")
                return None
            
            # Scale the features
            movie_features_scaled = _scaler.transform(movie_features)
        except KeyError as e:
            print(f"Error: Missing feature columns for '{movie_name}': {e}")
            return None
        except Exception as e:
            print(f"Error processing features for '{movie_name}': {e}")
            return None
        
        # Get recommendations
        distances, indices = _knn_model.kneighbors(movie_features_scaled)
        
        # Handle indices - it's a 2D array, we want the first row
        indices = indices[0]
        
    else:
        # Movie is in dataset
        movie_idx = movie_in_dataset.index[0]
        
        # Get the features for the input movie
        try:
            movie_features = _movie_data.iloc[movie_idx][_feature_columns].values.reshape(1, -1)
            
            # Check if we have valid features
            if len(movie_features) == 0 or movie_features.shape[1] == 0:
                print(f"Error: No valid features found for '{movie_name}'")
                return None
            
            # Scale the features
            movie_features_scaled = _scaler.transform(movie_features)
        except KeyError as e:
            print(f"Error: Missing feature columns for '{movie_name}': {e}")
            return None
        except Exception as e:
            print(f"Error processing features for '{movie_name}': {e}")
            return None
        
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
        recommended_movies = _movie_data.iloc[indices][['id', 'title', 'vote_average', 'vote_count', 'genre_ids', 'poster_path']]
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
    