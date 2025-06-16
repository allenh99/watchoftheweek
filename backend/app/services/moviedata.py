import os
import random
from dotenv import load_dotenv
import requests
from themoviedb import TMDb
import pandas as pd

load_dotenv()

# Path to the data directory
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

tmdb_api_key = os.getenv("TMDB_API_KEY")

tmdb = TMDb(key=tmdb_api_key, language="en-US")

#grab movie data from tmdb api
def get_movie_data(movie_id):
    try:
        movie = tmdb.movies(movie_id)
        movie_data = movie.info()
        return movie_data
    except Exception as e:
        print(f"Error fetching movie data: {e}")
        return None
    

def get_top_100_rated_movies():
    movies = []
    try:
        for i in range(5):
            movies_page = tmdb.movies().top_rated(page=i+1)
            for movie in movies_page.results:
                movies.append({
                    'id': movie.id,
                    'title': movie.original_title,
                    'genre_ids': movie.genre_ids,
                    'overview': movie.overview,
                    'release_date': movie.release_date,
                    'vote_average': movie.vote_average,
                    'vote_count': movie.vote_count,
                    'poster_path': movie.poster_path,
                    'original_language': movie.original_language
                })
    except Exception as e:
        print(f"Error fetching top movies: {e}")
        return None

    return pd.DataFrame(movies)

def get_top_100_popular_movies():
    movies = []
    try:
        for i in range(5):
            movies_page = tmdb.movies().popular(page=i+1)
            for movie in movies_page.results:
                movies.append({
                    'id': movie.id,
                    'title': movie.original_title,
                    'genre_ids': movie.genre_ids,
                    'overview': movie.overview,
                    'release_date': movie.release_date,
                    'vote_average': movie.vote_average,
                    'vote_count': movie.vote_count,
                    'poster_path': movie.poster_path,
                    'original_language': movie.original_language
                })
    except Exception as e:
        print(f"Error fetching popular movies: {e}")
        return None

    return pd.DataFrame(movies)

def export_movies_to_csv(df, filename='top_movies.csv'):
    """
    Export movie data to a CSV file in the data directory
    Args:
        df: pandas DataFrame containing movie data
        filename: name of the output CSV file
    """
    try:
        filepath = os.path.join(data_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Successfully exported movie data to {filepath}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")


df_top_rated = get_top_100_rated_movies()
df_popular = get_top_100_popular_movies()
if df_popular is not None:
    export_movies_to_csv(df_popular, 'top_popular_movies.csv')
if df_top_rated is not None:
    export_movies_to_csv(df_top_rated, 'top_rated_movies.csv')