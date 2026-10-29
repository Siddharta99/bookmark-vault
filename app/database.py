from sqlmodel import create_engine, Session
from app.config import DATABASE_URL  # Import the new variable

# Remove the old hardcoded sqlite string
engine = create_engine(DATABASE_URL) 

def get_session():
    with Session(engine) as session:
        yield session

from sqlmodel import create_engine, Session
from app.config import SECRET_KEY  # Test import works

engine = create_engine("sqlite:///bookmarks.db")

def get_session():
    with Session(engine) as session:
        yield session