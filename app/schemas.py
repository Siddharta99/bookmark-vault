from sqlmodel import SQLModel

class UserRegister(SQLModel):
    username: str
    email: str
    rawpassword: str

class UserLogin(SQLModel):
    username: str
    password: str

class BookmarkCreate(SQLModel):
    actual_url: str