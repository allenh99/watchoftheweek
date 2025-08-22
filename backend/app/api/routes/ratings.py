from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import Rating, Movie, User
from app.schemas.schemas import RatingCreate, RatingOut
from app.services.moviedata import get_movie_id_by_name, get_movie_data
from app.auth import get_current_user
from typing import List
import pandas as pd
import io

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#
@router.post("/ratings", response_model=RatingOut)
def create_rating(rating: RatingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Validate rating value
    if not (0.5 <= rating.rating <= 5.0):
        raise HTTPException(status_code=400, detail="Rating must be between 0.5 and 5.0")
    
    # Check if user already rated this movie
    existing_rating = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.movie_id == rating.movie_id
    ).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating.rating
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    else:
        # Create new rating
        new_rating = Rating(user_id=current_user.id, **rating.dict())
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating

@router.get("/ratings", response_model=List[RatingOut])
def get_ratings(db: Session = Depends(get_db)):
    # Filter out ratings where movie_id is None to prevent validation errors
    ratings = db.query(Rating).filter(Rating.movie_id.isnot(None)).all()
    return ratings


@router.post("/ratings/upload")
async def upload_ratings(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Read file into pandas DataFrame
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    successful_uploads = 0
    failed_uploads = 0
    failed_movies = []

    for _, row in df.iterrows():
        try:
            movie_name = row["Name"]
            #print(f"Processing movie: {movie_name}")
            movie_id = get_movie_id_by_name(movie_name)
            #print(f"Found movie ID: {movie_id}")
            
            if movie_id is None:
                failed_uploads += 1
                failed_movies.append(movie_name)
                #print(f"Failed to find movie ID for: {movie_name}")
                continue
            
            # Check if movie already exists in database
            existing_movie = db.query(Movie).filter(Movie.id == movie_id).first()
            print(f"Movie {movie_id} exists in DB: {existing_movie is not None}")
            
            if not existing_movie:
                # Get movie data from TMDB and create movie record
                movie_data = get_movie_data(movie_id)
                if movie_data:
                    genre_ids = movie_data.get('genre_ids', [])
                    if genre_ids is None:
                        genre_ids = []
                    
                    # Safely handle release_date which might be a datetime.date object
                    release_date = movie_data.get('release_date')
                    year = None
                    if release_date:
                        if isinstance(release_date, str):
                            year = int(release_date[:4]) if len(release_date) >= 4 else None
                        else:
                            # Handle datetime.date object
                            year = release_date.year
                    
                    movie = Movie(
                        id=movie_data['id'],
                        title=movie_data['title'],
                        genre=", ".join([str(g) for g in genre_ids]),
                        director="Unknown",  # TMDB doesn't provide director in basic movie data
                        year=year
                    )
                    db.add(movie)
                    print(f"Created movie record: {movie.title} (ID: {movie.id})")
                else:
                    # Create a basic movie record if TMDB data fetch fails
                    movie = Movie(
                        id=movie_id,
                        title=movie_name,
                        genre="Unknown",
                        director="Unknown",
                        year=None
                    )
                    db.add(movie)
                    print(f"Created basic movie record: {movie_name} (ID: {movie_id})")
            else:
                print(f"Movie already exists: {existing_movie.title} (ID: {movie_id})")
                
            # Check if user already has a rating for this movie
            existing_rating = db.query(Rating).filter(
                Rating.user_id == current_user.id,
                Rating.movie_id == movie_id
            ).first()
            
            if existing_rating:
                # Update existing rating
                existing_rating.rating = row["Rating"]
                print(f"Updated rating for {movie_name}: {row['Rating']}/5")
            else:
                # Create new rating
                rating = Rating(
                    user_id=current_user.id,
                    movie_id=movie_id,
                    rating=row["Rating"]
                )
                db.add(rating)
                print(f"Created new rating for {movie_name}: {row['Rating']}/5")
            
            successful_uploads += 1
            
            # Commit after each movie to avoid transaction issues
            db.commit()
            print(f"Successfully processed: {movie_name}")
            
        except Exception as e:
            print(f"Error processing {movie_name}: {e}")
            db.rollback()
            failed_uploads += 1
            failed_movies.append(movie_name)
            continue

    return {
        "message": f"Upload completed for user {current_user.username}",
        "successful_uploads": successful_uploads,
        "failed_uploads": failed_uploads,
        "failed_movies": failed_movies
    }