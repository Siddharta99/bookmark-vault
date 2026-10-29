from fastapi import FastAPI
from sqlmodel import SQLModel

# Import our database engine to ensure tables can be created
from app.database import engine

# Import our routers
from app.routers import auth, bookmarks

app = FastAPI(title="Bookmark Vault API")

# Include routers
app.include_router(auth.router)
app.include_router(bookmarks.router)

# Create tables on startup
SQLModel.metadata.create_all(engine)