import os

# Read from Environment Variable (Render), fallback to default for local dev
SECRET_KEY = os.getenv("SECRET_KEY", "bookmark-vault-wax-555")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database URL logic we added earlier
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bookmarks.db")