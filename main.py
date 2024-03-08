from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models as models
from database import engine
from routers import blog, user, authentication, comments
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Configure CORS
origins = ["http://localhost:3000", "https://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(blog.router)
app.include_router(comments.router)
