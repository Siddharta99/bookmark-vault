from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
import jwt
import hashlib, secrets
from datetime import datetime, timedelta, timezone

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_session
from app.models import User
from app.schemas import UserRegister, UserLogin

router = APIRouter()

def hash_password(password: str):
    salt = secrets.token_hex(16)
    grind = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return salt + ":" + grind.hex()

@router.post("/users")
def register_user(payload: UserRegister, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == payload.username)).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Username taken")
    hashed_pw = hash_password(payload.rawpassword)
    new_user = User(username=payload.username, email=payload.email, hashed_password=hashed_pw)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "Registered!", "id": new_user.id}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
def login_user(payload: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == payload.username)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    stored_fingerprint = user.hashed_password
    salt, stored_hash = stored_fingerprint.split(":")
    new_hash = hashlib.pbkdf2_hmac("sha256", payload.password.encode(), salt.encode(), 100_000).hex()
    if new_hash == stored_hash:
        token = create_access_token(data={"user_id": user.id})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")