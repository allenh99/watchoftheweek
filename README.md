# Movie Recommendations System

A full-stack movie recommendation application that provides personalized movie suggestions based on user ratings and collaborative filtering algorithms.

## Features

- **Personalized Recommendations**: Get movie suggestions based on your rating history
- **Machine Learning Pipeline**: K-Nearest Neighbors algorithm for content-based filtering
- **Real-time Movie Data**: Integration with The Movie Database (TMDB) API
- **User Rating System**: Rate movies and build your personal movie profile
- **Modern Web Interface**: Responsive Next.js frontend with Tailwind CSS
- **RESTful API**: FastAPI backend with comprehensive endpoints

## Architecture

### Backend (FastAPI + SQLAlchemy)
- **Framework**: FastAPI with automatic API documentation
- **Database**: SQLite with SQLAlchemy ORM
- **ML Pipeline**: scikit-learn with K-Nearest Neighbors algorithm
- **External APIs**: The Movie Database (TMDB) integration
- **Features**: User management, rating system, recommendation engine

### Frontend (Next.js)
- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS for responsive design
- **Language**: TypeScript for type safety
- **State Management**: React hooks for client-side state

## Endpoints

### Recommendations
- `GET /api/recommendations/{user_id}` - Get personalized movie recommendations
- `GET /api/user-top-movies/{user_id}` - Get user's top-rated movies

### Ratings
- `POST /api/ratings` - Add a new movie rating
- `GET /api/ratings/{user_id}` - Get user's rating history

## Database Schema

### Users
- `id` (Primary Key)
- `email` (Unique)

### Movies
- `id` (Primary Key)
- `title`
- `genre`
- `director`
- `year`

### Ratings
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `movie_id` (Foreign Key)
- `rating` (Float)

## 🛠️ Development

### Project Structure
```
movie-recs/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # API endpoints
│   │   ├── ml_models/      # ML pipeline
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── data/          # Movie datasets
│   ├── db_tools/          # Database utilities
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── app/           # Next.js app router
    │   └── components/    # React components
    └── package.json
```

### Key Technologies
- **Backend**: FastAPI, SQLAlchemy, scikit-learn, pandas, numpy
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Database**: SQLite
- **External APIs**: The Movie Database (TMDB)
