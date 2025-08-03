from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    # Weekly recommendation fields
    weekly_recommendation_id = Column(Integer, nullable=True)
    weekly_recommendation_date = Column(DateTime, nullable=True)
    ratings = relationship("Rating", back_populates="user")

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    genre = Column(String)
    director = Column(String)
    year = Column(Integer)
    

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    rating = Column(Float)

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie")
