from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str
    hashed_password: str

class Bookmark(SQLModel, table=True):
    __tablename__ = "bookmarks"
    id: int | None = Field(default=None, primary_key=True)
    actual_url: str
    owner_id: int = Field(foreign_key="users.id")