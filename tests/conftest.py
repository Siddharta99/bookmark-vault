import warnings
warnings.filterwarnings("ignore", message=".*HMAC key is.*")

import pytest
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session

# Use a separate in-memory SQLite DB for tests so we don't touch bookmarks.db
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(scope="function")
def client():
    """Creates a fresh test client and resets the DB for every test."""
    
    # Drop all tables and recreate them (Clean Slate)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    # Tell the app to use our TEST engine instead of the real one
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as c:
        yield c
        
    # Cleanup overrides after test finishes
    app.dependency_overrides.clear()