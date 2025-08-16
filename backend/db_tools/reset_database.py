import os
import sys
# Add the parent directory (backend) to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, inspect, text
from app.database import Base
from app.models.models import User, Movie, Rating, Recommendation

def reset_database():
    """Reset the database by dropping all tables and recreating them"""
    
    # Database URL - adjust this to match your actual database path
    DATABASE_URL = "sqlite:///./app.db"
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    print("Dropping all tables...")
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables...")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database reset complete!")
    print("All tables have been dropped and recreated.")

def check_database_schema():
    """Check if the database schema matches the models"""
    
    DATABASE_URL = "sqlite:///./app.db"
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    print("Checking database schema...")
    
    # Check movies table
    if 'movies' in inspector.get_table_names():
        movie_columns = [col['name'] for col in inspector.get_columns('movies')]
        print(f"Movies table columns: {movie_columns}")
        
        expected_columns = ['id', 'title', 'genre', 'director', 'year']
        missing_columns = [col for col in expected_columns if col not in movie_columns]
        
        if missing_columns:
            print(f"Missing columns in movies table: {missing_columns}")
            return False
        else:
            print("Movies table schema is correct!")
    else:
        print("Movies table does not exist!")
        return False
    
    # Check recommendations table
    if 'recommendations' in inspector.get_table_names():
        recommendation_columns = [col['name'] for col in inspector.get_columns('recommendations')]
        print(f"Recommendations table columns: {recommendation_columns}")
        
        expected_columns = ['id', 'user_id', 'movie_id', 'source_movies', 'time_generated']
        missing_columns = [col for col in expected_columns if col not in recommendation_columns]
        
        if missing_columns:
            print(f"Missing columns in recommendations table: {missing_columns}")
            return False
        else:
            print("Recommendations table schema is correct!")
    else:
        print("Recommendations table does not exist!")
        return False
    
    return True

def delete_database_file():
    """Delete the database file completely"""
    
    db_file = "./app.db"
    
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Database file '{db_file}' has been deleted.")
    else:
        print(f"Database file '{db_file}' not found.")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Reset database (drop and recreate tables)")
    print("2. Delete database file completely")
    print("3. Check database schema")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        reset_database()
    elif choice == "2":
        delete_database_file()
    elif choice == "3":
        check_database_schema()
    else:
        print("Invalid choice. Please run the script again.") 