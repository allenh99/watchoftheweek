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
        movie = tmdb.movie(movie_id).details()
        credits = tmdb.movie(movie_id).credits()
        

        cast = credits.cast[:3] if credits.cast else []
        cast_names = [person.name for person in cast]
        
        director = None
        for person in credits.crew:
            if person.job == "Director":
                director = person.name
                break
        
        return {
            'id': movie.id,
            'title': movie.original_title,
            'genre_ids': movie.genre_ids,
            'overview': movie.overview,
            'release_date': movie.release_date,
            'vote_average': movie.vote_average,
            'vote_count': movie.vote_count,
            'poster_path': movie.poster_path,
            'original_language': movie.original_language,
            'cast': cast_names,
            'director': director
        }
    except Exception as e:
        print(f"Error fetching movie data: {e}")
        return None
    

def get_top_100_rated_movies():
    movies = []
    try:
        for i in range(5):
            movies_page = tmdb.movies().top_rated(page=i+1)
            for movie in movies_page.results:
                # Get detailed movie data including cast and director
                detailed_movie = get_movie_data(movie.id)
                if detailed_movie:
                    movies.append(detailed_movie)
                else:
                    # Fallback to basic data if detailed fetch fails
                    movies.append({
                        'id': movie.id,
                        'title': movie.original_title,
                        'genre_ids': movie.genre_ids,
                        'overview': movie.overview,
                        'release_date': movie.release_date,
                        'vote_average': movie.vote_average,
                        'vote_count': movie.vote_count,
                        'poster_path': movie.poster_path,
                        'original_language': movie.original_language,
                        'cast': [],
                        'director': None
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
                # Get detailed movie data including cast and director
                detailed_movie = get_movie_data(movie.id)
                if detailed_movie:
                    movies.append(detailed_movie)
                else:
                    movies.append({
                        'id': movie.id,
                        'title': movie.original_title,
                        'genre_ids': movie.genre_ids,
                        'overview': movie.overview,
                        'release_date': movie.release_date,
                        'vote_average': movie.vote_average,
                        'vote_count': movie.vote_count,
                        'poster_path': movie.poster_path,
                        'original_language': movie.original_language,
                        'cast': [],
                        'director': None
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

def get_movie_id_by_name(movie_name):
    """
    Search for a movie by name and return its TMDB ID
    Args:
        movie_name: The name of the movie to search for
    Returns:
        int: The TMDB ID of the movie if found, None otherwise
    """
    try:
        search_results = tmdb.search().movies(query=movie_name)
        if search_results and len(search_results.results) > 0:
            return search_results.results[0].id
        return None
    except Exception as e:
        print(f"Error searching for movie: {e}")
        return None




# print("Regenerating movie dataset with enhanced features...")
# print("This will take a few minutes as we fetch detailed data for each movie...")

# df_top_rated = get_top_100_rated_movies()
# df_popular = get_top_100_popular_movies()

# if df_popular is not None:
#     print(f"Successfully fetched {len(df_popular)} popular movies")
#     export_movies_to_csv(df_popular, 'top_popular_movies.csv')
# else:
#     print("Failed to fetch popular movies")

# if df_top_rated is not None:
#     print(f"Successfully fetched {len(df_top_rated)} top rated movies")
#     export_movies_to_csv(df_top_rated, 'top_rated_movies.csv')
# else:
#     print("Failed to fetch top rated movies")

# print("Dataset regeneration complete!")
# print("New features included:")
# print("- Original language (one-hot encoded)")
# print("- Top 3 cast members (one-hot encoded)")
# print("- Director (one-hot encoded)")
# print("- All previous features (genres, ratings, etc.)")

#TESTING METHODS CODE
#print(get_movie_id_by_name("The Dark Knight"))
# print(get_movie_data(155))
