import sys
import os
# Add the parent directory (backend) to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.models import User, Movie, Rating
from app.services.recommender import recommend, get_user_top_movies
import pandas as pd

def create_test_data(db_session):
    """Create test users, movies, and ratings"""
    
    # Create test users
    user1 = User(email="test1@example.com")
    user2 = User(email="test2@example.com")
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()
    
    # Create test movies
    movies_data = [
        {"title": "The Dark Knight", "genre": "Action", "director": "Christopher Nolan", "year": 2008},
        {"title": "Inception", "genre": "Sci-Fi", "director": "Christopher Nolan", "year": 2010},
        {"title": "Interstellar", "genre": "Sci-Fi", "director": "Christopher Nolan", "year": 2014},
        {"title": "The Matrix", "genre": "Sci-Fi", "director": "Wachowski Sisters", "year": 1999},
        {"title": "Pulp Fiction", "genre": "Crime", "director": "Quentin Tarantino", "year": 1994},
        {"title": "Fight Club", "genre": "Drama", "director": "David Fincher", "year": 1999},
        {"title": "Forrest Gump", "genre": "Drama", "director": "Robert Zemeckis", "year": 1994},
        {"title": "The Shawshank Redemption", "genre": "Drama", "director": "Frank Darabont", "year": 1994},
        {"title": "Goodfellas", "genre": "Crime", "director": "Martin Scorsese", "year": 1990},
        {"title": "The Godfather", "genre": "Crime", "director": "Francis Ford Coppola", "year": 1972}
    ]
    
    movies = []
    for movie_data in movies_data:
        movie = Movie(**movie_data)
        db_session.add(movie)
        movies.append(movie)
    db_session.commit()
    
    # Create test ratings for user1 (likes action/sci-fi movies)
    user1_ratings = [
        (movies[0].id, 9.0),  # The Dark Knight
        (movies[1].id, 8.5),  # Inception
        (movies[2].id, 8.0),  # Interstellar
        (movies[3].id, 9.5),  # The Matrix
        (movies[6].id, 7.0),  # Forrest Gump
    ]
    
    for movie_id, rating in user1_ratings:
        rating_obj = Rating(user_id=user1.id, movie_id=movie_id, rating=rating)
        db_session.add(rating_obj)
    
    # Create test ratings for user2 (likes crime/drama movies)
    user2_ratings = [
        (movies[4].id, 9.0),  # Pulp Fiction
        (movies[5].id, 8.5),  # Fight Club
        (movies[7].id, 9.5),  # The Shawshank Redemption
        (movies[8].id, 8.0),  # Goodfellas
        (movies[9].id, 9.0),  # The Godfather
    ]
    
    for movie_id, rating in user2_ratings:
        rating_obj = Rating(user_id=user2.id, movie_id=movie_id, rating=rating)
        db_session.add(rating_obj)
    
    db_session.commit()
    return user1.id, user2.id

def test_recommendation_system():
    """Test the recommendation system"""
    
    # Create database connection
    DATABASE_URL = "sqlite:///./test_movies.db"
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    
    try:
        print("Creating test data...")
        user1_id, user2_id = create_test_data(db_session)
        
        print(f"\n=== Testing User {user1_id} (Action/Sci-Fi lover) ===")
        
        # Get user's top movies
        top_movies = get_user_top_movies(user1_id, db_session, top_n=5)
        print("\nUser's top-rated movies:")
        for movie in top_movies:
            print(f"- {movie['title']} (Rating: {movie['rating']})")
        
        # Get recommendations
        print("\nGetting recommendations...")
        recommendations = recommend(user1_id, db_session, top_n=10)
        
        if not recommendations.empty:
            print("\nTop recommendations:")
            for idx, row in recommendations.head(5).iterrows():
                print(f"{idx+1}. {row['title']} (Score: {row['weighted_score']:.2f})")
                print(f"   Based on: {', '.join(row['source_movie'])}")
                print(f"   TMDB Rating: {row['vote_average']}")
        else:
            print("No recommendations found")
        
        print(f"\n=== Testing User {user2_id} (Crime/Drama lover) ===")
        
        # Get user's top movies
        top_movies = get_user_top_movies(user2_id, db_session, top_n=5)
        print("\nUser's top-rated movies:")
        for movie in top_movies:
            print(f"- {movie['title']} (Rating: {movie['rating']})")
        
        # Get recommendations
        print("\nGetting recommendations...")
        recommendations = recommend(user2_id, db_session, top_n=10)
        
        if not recommendations.empty:
            print("\nTop recommendations:")
            for idx, row in recommendations.head(5).iterrows():
                print(f"{idx+1}. {row['title']} (Score: {row['weighted_score']:.2f})")
                print(f"   Based on: {', '.join(row['source_movie'])}")
                print(f"   TMDB Rating: {row['vote_average']}")
        else:
            print("No recommendations found")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_session.close()
        # Clean up test database
        if os.path.exists("./test_movies.db"):
            os.remove("./test_movies.db")

if __name__ == "__main__":
    test_recommendation_system() 