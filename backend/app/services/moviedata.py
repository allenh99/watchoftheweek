import os
import random
from dotenv import load_dotenv
import requests
from themoviedb import TMDb

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
    

def get_top_100_movies():
    movies = []
    try:
        for i in range(5):
            movies_page = tmdb.movies().top_rated(page=i+1)
            movies.extend(movies_page)
        #print(movies)
        return movies
    except Exception as e:
        print(f"Error fetching top 1000 movies: {e}")
        return None

print(len(get_top_1000_movies()))