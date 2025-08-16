import os
import sys
# Add the parent directory (backend) to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, inspect, text
from app.database import SessionLocal
from app.models.models import User, Movie, Rating, Recommendation

def view_database_contents():
    """View the contents of all database tables"""
    
    db = SessionLocal()
    
    try:
        print("=" * 50)
        print("DATABASE CONTENTS")
        print("=" * 50)
        
        # Check Users table
        print("\n📋 USERS TABLE:")
        users = db.query(User).all()
        if users:
            for user in users:
                print(f"  ID: {user.id}, Username: {user.username}, Email: {user.email}")
        else:
            print("  No users found")
        
        # Check Movies table
        print("\n🎬 MOVIES TABLE:")
        movies = db.query(Movie).limit(10).all()  # Show first 10 movies
        if movies:
            for movie in movies:
                print(f"  ID: {movie.id}, Title: {movie.title}, Year: {movie.year}")
            total_movies = db.query(Movie).count()
            print(f"  Total movies in database: {total_movies}")
        else:
            print("  No movies found")
        
        # Check Ratings table
        print("\n⭐ RATINGS TABLE:")
        ratings = db.query(Rating).limit(10).all()  # Show first 10 ratings
        if ratings:
            for rating in ratings:
                print(f"  User ID: {rating.user_id}, Movie ID: {rating.movie_id}, Rating: {rating.rating}")
            total_ratings = db.query(Rating).count()
            print(f"  Total ratings in database: {total_ratings}")
        else:
            print("  No ratings found")
        
        # Check Recommendations table
        print("\n🎯 RECOMMENDATIONS TABLE:")
        recommendations = db.query(Recommendation).all()
        if recommendations:
            for rec in recommendations:
                print(f"  User ID: {rec.user_id}, Movie ID: {rec.movie_id}, Generated: {rec.time_generated}")
            total_recommendations = db.query(Recommendation).count()
            print(f"  Total recommendations in database: {total_recommendations}")
        else:
            print("  No recommendations found")
        
        # Check specific user ratings
        print("\n🔍 DETAILED USER RATINGS:")
        users_with_ratings = db.query(User).join(Rating).distinct().all()
        if users_with_ratings:
            for user in users_with_ratings:
                user_ratings = db.query(Rating).filter(Rating.user_id == user.id).all()
                print(f"  User {user.username} (ID: {user.id}) has {len(user_ratings)} ratings:")
                for rating in user_ratings[:5]:  # Show first 5 ratings per user
                    movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
                    movie_title = movie.title if movie else f"Movie ID {rating.movie_id}"
                    print(f"    - {movie_title}: {rating.rating}/5")
                if len(user_ratings) > 5:
                    print(f"    ... and {len(user_ratings) - 5} more ratings")
        else:
            print("  No users with ratings found")
        
    except Exception as e:
        print(f"Error viewing database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_user_ratings(user_id: int):
    """Check ratings for a specific user"""
    
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"User with ID {user_id} not found")
            return
        
        print(f"\n🔍 RATINGS FOR USER {user.username} (ID: {user_id}):")
        
        ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
        if ratings:
            print(f"User has {len(ratings)} ratings:")
            for rating in ratings:
                movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
                movie_title = movie.title if movie else f"Movie ID {rating.movie_id}"
                print(f"  - {movie_title}: {rating.rating}/5")
        else:
            print("User has no ratings")
        
        # Check recommendations for this user
        recommendations = db.query(Recommendation).filter(Recommendation.user_id == user_id).all()
        if recommendations:
            print(f"\nUser has {len(recommendations)} recommendations:")
            for rec in recommendations:
                movie = db.query(Movie).filter(Movie.id == rec.movie_id).first()
                movie_title = movie.title if movie else f"Movie ID {rec.movie_id}"
                print(f"  - {movie_title} (generated: {rec.time_generated})")
        else:
            print("User has no recommendations")
            
    except Exception as e:
        print(f"Error checking user ratings: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Choose an option:")
    print("1. View all database contents")
    print("2. Check ratings for specific user")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        view_database_contents()
    elif choice == "2":
        user_id = input("Enter user ID: ").strip()
        try:
            check_user_ratings(int(user_id))
        except ValueError:
            print("Invalid user ID. Please enter a number.")
    else:
        print("Invalid choice. Please run the script again.")
