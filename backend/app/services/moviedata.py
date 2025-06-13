import os
import random
from dotenv import load_dotenv
import requests
from themoviedb import TMDb
import pandas as pd

load_dotenv()

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
    Export movie data to a CSV file
    Args:
        df: pandas DataFrame containing movie data
        filename: name of the output CSV file
    """
    try:
        df.to_csv(filename, index=False)
        print(f"Successfully exported movie data to {filename}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")

# Example usage:
df = get_top_100_popular_movies()
print(df)
# if df is not None:
#     export_movies_to_csv(df)

# Example usage:
# df_top_rated = get_top_100_movies()
# df_popular = get_popular_movies()
# if df_popular is not None:
#     export_movies_to_csv(df_popular, 'popular_movies.csv')