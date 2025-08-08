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
            # 'vote_average': movie.vote_average,
            # 'vote_count': movie.vote_count,
            'poster_path': movie.poster_path,
            'original_language': movie.original_language,
            'cast': cast_names,
            'director': director,
            'backdrop_path': movie.backdrop_path,
            'runtime': movie.runtime,
            'release_date': movie.release_date,
            'tagline': movie.tagline
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

def convert_films_txt_to_csv():
    """
    Convert films.txt to CSV format using existing TMDB setup
    """
    import csv
    import os
    
    # Read films.txt
    films_file = os.path.join(data_dir, 'films.txt')
    output_file = os.path.join(data_dir, 'films.csv')
    
    if not os.path.exists(films_file):
        print(f"Error: {films_file} not found")
        return
    
    # Read movie titles
    with open(films_file, 'r', encoding='utf-8') as f:
        movie_titles = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(movie_titles)} movies in {films_file}")
    
    # CSV headers matching the existing structure
    headers = [
        'id', 'title', 'genre_ids', 'overview', 'release_date', 
        'vote_average', 'vote_count', 'poster_path', 'original_language',
        'cast', 'director'
    ]
    
    # Prepare CSV data
    csv_data = []
    
    for i, title in enumerate(movie_titles, 1):
        print(f"Processing {i}/{len(movie_titles)}: {title}")
        
        try:
            # Search for movie using existing method
            movie_id = get_movie_id_by_name(title)
            
            if movie_id:
                # Get detailed movie data using existing method
                movie_data = get_movie_data(movie_id)
                
                if movie_data:
                    # Convert cast list to string format
                    cast_str = str(movie_data['cast']) if movie_data['cast'] else '[]'
                    
                    # Prepare row data
                    row = {
                        'id': movie_data['id'],
                        'title': movie_data['title'],
                        'genre_ids': str(movie_data['genre_ids']),
                        'overview': movie_data['overview'],
                        'release_date': movie_data['release_date'],
                        'vote_average': movie_data['vote_average'],
                        'vote_count': movie_data['vote_count'],
                        'poster_path': movie_data['poster_path'],
                        'original_language': movie_data['original_language'],
                        'cast': cast_str,
                        'director': movie_data['director']
                    }
                    
                    csv_data.append(row)
                    print(f"  ✓ Found: {movie_data['title']} ({movie_data['release_date']})")
                else:
                    print(f"  ✗ Could not get details for: {title}")
            else:
                print(f"  ✗ Not found: {title}")
                
        except Exception as e:
            print(f"  ✗ Error processing {title}: {e}")
        
        # Rate limiting - be nice to the API
        import time
        time.sleep(0.25)
    
    # Write CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"\nConversion complete! Created {output_file} with {len(csv_data)} movies")

#TESTING METHODS CODE
#print(get_movie_id_by_name("The Dark Knight"))
# print(get_movie_data(155))

def get_movie_streaming_data(movie_id):
    country = "US"
    streamingdata = {
        'flatrate': [],
        'free': [],
        'ads': [],
        'buy': [],
        'rent': []
    }
    try:
        watch_providers = tmdb.watch_providers().movie(country)
        #print(watch_providers)
        movies = tmdb.movie(movie_id).watch_providers().results[country]
        if movies.flatrate:
            for i in movies.flatrate:
                streamingdata['flatrate'].append((i.provider_name, i.provider_id, i.logo_path))
        if movies.free:
            for i in movies.free:
                streamingdata['free'].append((i.provider_name, i.provider_id, i.logo_path))
        if movies.ads:
            for i in movies.ads:
                streamingdata['ads'].append((i.provider_name, i.provider_id, i.logo_path))
        if movies.buy:
            for i in movies.buy:
                streamingdata['buy'].append((i.provider_name, i.provider_id, i.logo_path))
        if movies.rent:
            for i in movies.rent:
                streamingdata['rent'].append((i.provider_name, i.provider_id, i.logo_path))
        print(streamingdata)
        return streamingdata
    except Exception as e:
        print(f"Error fetching movie streaming data: {e}")
        return None