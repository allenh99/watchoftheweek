from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import ratings, recommend
from app.database import Base, engine
from app.models import models

app = FastAPI()

# DB setup
models.Base.metadata.create_all(bind=engine)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ratings.router, prefix="/api")
app.include_router(recommend.router, prefix="/api")