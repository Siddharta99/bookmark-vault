import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bookmarks.db")

SECRET_KEY = "bookmark-vault-wax-555"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30