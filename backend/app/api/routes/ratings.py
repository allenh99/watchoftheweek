from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import Rating, Movie
from app.schemas.schemas import RatingCreate, RatingOut
from app.services.moviedata import get_movie_id_by_name, get_movie_data
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
def create_rating(rating: RatingCreate, db: Session = Depends(get_db)):
    new_rating = Rating(user_id=1, **rating.dict())  # Hardcoded user
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
async def upload_ratings(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Read file into pandas DataFrame
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    successful_uploads = 0
    failed_uploads = 0
    failed_movies = []

    for _, row in df.iterrows():
        movie_name = row["Name"]
        movie_id = get_movie_id_by_name(movie_name)
        
        if movie_id is None:
            failed_uploads += 1
            failed_movies.append(movie_name)
            continue
        
        # Check if movie already exists in database
        existing_movie = db.query(Movie).filter(Movie.id == movie_id).first()
        
        if not existing_movie:
            # Get movie data from TMDB and create movie record
            movie_data = get_movie_data(movie_id)
            if movie_data:
                movie = Movie(
                    id=movie_data['id'],
                    title=movie_data['title'],
                    genre=", ".join([str(g) for g in movie_data.get('genre_ids', [])]),
                    director="Unknown",  # TMDB doesn't provide director in basic movie data
                    year=int(movie_data.get('release_date', '0')[:4]) if movie_data.get('release_date') else None
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
            
        rating = Rating(
            user_id=user_id,
            movie_id=movie_id,
            rating=row["Rating"]
        )
        db.add(rating)
        successful_uploads += 1
    
    db.commit()

    return {
        "message": f"Upload completed for user {user_id}",
        "successful_uploads": successful_uploads,
        "failed_uploads": failed_uploads,
        "failed_movies": failed_movies
    }