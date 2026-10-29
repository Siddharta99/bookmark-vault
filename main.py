from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Field, create_engine, Session, select, SQLModel # Fix the blank!
import jwt
import hashlib, secrets
from datetime import datetime, timedelta, timezone

SECRET_KEY = "bookmark-vault-wax-555" # Put a real secret string here
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

engine = create_engine("sqlite:///bookmarks.db") # Fix the filename!
app = FastAPI()

class User(SQLModel,table=True):
    __tablename__ = "users"
    id:int | None = Field(default=None,primary_key=True)
    username:str = Field(index=True,unique=True)
    email:str
    hashed_password:str

class UserRegister(SQLModel):
    username: str
    email: str
    rawpassword: str

class UserLogin(SQLModel):
    username:str
    password:str

class Bookmark(SQLModel,table=True):
    __tablename__ = "bookmarks"
    id:int | None = Field(default=None,primary_key=True)
    actual_url:str
    owner_id: int = Field(foreign_key="users.id")

class BookmarkCreate(SQLModel):
    actual_url:str
    
def hash_password(password: str):
    # 1. Grab a random 16-byte salt
    salt = secrets.token_hex(16)
    # 2. Grind the password + salt 100,000 times using SHA256
    grind = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    # 3. Return the combined fingerprint (salt:grind)
    return salt + ":" + grind.hex()

@app.post("/users")
def register_user(payload:UserRegister):
    with Session(engine) as  session:
        existing_user = session.exec(select(User).where(User.username == payload.username)).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Username taken")
        hashed_pw = hash_password(payload.rawpassword)
        new_user = User(username=payload.username,email=payload.email,hashed_password=hashed_pw)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"message": "Registered!", "id": new_user.id}
    
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
@app.post("/login")
def login_user(payload: UserLogin):
    with Session(engine) as session:
        
        # STEP 1: Find the user by username
        user = session.exec(select(User).where(User.username == payload.username)).first() # Hint: select(User)... .first()
        
        # GUARD: If user is None, raise 401 error here
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        
        # STEP 2: Get the stored fingerprint from the 'user' object
        stored_fingerprint = user.hashed_password
        
        # Split it into salt and stored_hash
        salt, stored_hash =stored_fingerprint.split(":") # Hint: .split(":")
        
        # STEP 3: Re-create the hash using payload.password AND the extracted salt
        # (Use hashlib.pbkdf2_hmac like we practiced earlier)
        new_hash = hashlib.pbkdf2_hmac("sha256",payload.password.encode(),salt.encode(),100_000).hex()
        
        # STEP 4: Compare new_hash with stored_hash
        if new_hash == stored_hash: 
            
            # SUCCESS: Generate JWT token here (use jwt.encode)
            token = create_access_token(data={"user_id": user.id})
            return {"access_token": token, "token_type": "bearer"}

        else:
            # FAILURE: Raise 401 error
            raise HTTPException(status_code=401, detail="Invalid credentials")
           
def get_session():
    with Session(engine) as session:
        yield session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # FastAPI's automatic envelope opener

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        # 1. Decode the token using the SECRET_KEY and ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # 2. Extract the user_id from the decoded payload dictionary
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        # 3. Fetch the user from DB and return them (Step 4)
        user = session.exec(select(User).where(User.id == user_id)).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
        
    except jwt.PyJWTError:
        # 4. If the token is fake or expired (Step 3)
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.post("/bookmarks")
def create_bookmark(
    payload: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # 3. The Logic (Build the object using the verified Bouncer data)
    new_bookmark = Bookmark(
        actual_url=payload.actual_url, #here we get the URL?
        owner_id=current_user.id# Where do we get the SAFE owner ID?
    )

    # 4. The Database Save
    session.add(new_bookmark)
    session.commit()
    session.refresh(new_bookmark)

    return new_bookmark

@app.get("/bookmarks/mine")
def read_my_bookmarks(
    current_user: User = Depends(get_current_user), # 1. Who is asking?
    session: Session = Depends(get_session)         # 2. Open DB connection
):
    # 3. QUERY: Find all bookmarks owned by THIS specific user
    my_bookmarks = session.exec(
        select(Bookmark)                     # Which table/class are we selecting from?
        .where(Bookmark.owner_id == current_user.id)              # Filter condition: Column == Value
    ).all()                             # Get ALL matching rows (not just first())

    # 4. RETURN
    return my_bookmarks

@app.delete("/bookmarks/{bookmark_id}")
def delete_bookmark(
    bookmark_id: int,                   # Path parameter
    current_user: User = Depends(get_current_user),  # Lock 1: Who is asking?
    session: Session = Depends(get_session)
):
    # Lock 2a: Fetch the bookmark
    bookmark = session.exec(
        select(Bookmark).where(Bookmark.id == bookmark_id)
    ).first()

    # Lock 2b: Does it exist?
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    # Lock 2c: Does THIS user own it?
    if bookmark.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Safe to delete
    session.delete(bookmark)
    session.commit()
    return {"message": "Deleted"}

@app.patch("/bookmarks/{bookmark_id}")
def update_bookmark(
    bookmark_id: int,
    payload: BookmarkCreate,            # Reuse the same capsule (only url)
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Lock 2a: Fetch
    bookmark = session.exec(
        select(Bookmark).where(Bookmark.id == bookmark_id)
    ).first()

    # Lock 2b: Exists?
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    # Lock 2c: Ownership?
    if bookmark.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update & Save
    bookmark.actual_url = payload.actual_url
    session.add(bookmark)
    session.commit()
    session.refresh(bookmark)
    return bookmark

SQLModel.metadata.create_all(engine)
