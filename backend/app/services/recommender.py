from app.models.models import Rating, Movie
from sqlalchemy.orm import Session

#recommend a user movies based on genre, leads, director -> from tmdb api
def recommend(user: int):
    return 