import os
import sys
# Add the parent directory (backend) to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, inspect, text
from app.database import SessionLocal
from app.models.models import Movie

def check_movies():
    """Check if there are any movies in the database"""
    
    db = SessionLocal()
    
    try:
        print("Checking movies table...")
        
        # Check if movies table exists
        inspector = inspect(db.bind)
        if 'movies' not in inspector.get_table_names():
            print("❌ Movies table does not exist!")
            return
        
        # Count movies
        movie_count = db.query(Movie).count()
        print(f"📊 Total movies in database: {movie_count}")
        
        if movie_count > 0:
            print("\n🎬 Movies in database:")
            movies = db.query(Movie).limit(20).all()  # Show first 20
            for movie in movies:
                print(f"  ID: {movie.id}, Title: {movie.title}")
            
            if movie_count > 20:
                print(f"  ... and {movie_count - 20} more movies")
        else:
            print("✅ Movies table is empty")
        
        # Check for specific movie IDs that were mentioned in the error
        problematic_ids = [155, 10681, 546554, 545611, 370172, 566525, 640, 272]
        print(f"\n🔍 Checking for problematic movie IDs: {problematic_ids}")
        
        for movie_id in problematic_ids:
            movie = db.query(Movie).filter(Movie.id == movie_id).first()
            if movie:
                print(f"  ❌ Movie ID {movie_id} exists: {movie.title}")
            else:
                print(f"  ✅ Movie ID {movie_id} does not exist")
        
    except Exception as e:
        print(f"Error checking movies: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_movies()
