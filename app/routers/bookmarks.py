from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
import jwt

from app.config import SECRET_KEY, ALGORITHM
from app.database import get_session
from app.models import User, Bookmark
from app.schemas import BookmarkCreate

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = session.exec(select(User).where(User.id == user_id)).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.post("/bookmarks")
def create_bookmark(
    payload: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    new_bookmark = Bookmark(actual_url=payload.actual_url, owner_id=current_user.id)
    session.add(new_bookmark)
    session.commit()
    session.refresh(new_bookmark)
    return new_bookmark

@router.get("/bookmarks/mine")
def read_my_bookmarks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    my_bookmarks = session.exec(
        select(Bookmark).where(Bookmark.owner_id == current_user.id)
    ).all()
    return my_bookmarks

@router.delete("/bookmarks/{bookmark_id}")
def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    bookmark = session.exec(select(Bookmark).where(Bookmark.id == bookmark_id)).first()
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    if bookmark.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    session.delete(bookmark)
    session.commit()
    return {"message": "Deleted"}

@router.patch("/bookmarks/{bookmark_id}")
def update_bookmark(
    bookmark_id: int,
    payload: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    bookmark = session.exec(select(Bookmark).where(Bookmark.id == bookmark_id)).first()
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    if bookmark.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    bookmark.actual_url = payload.actual_url
    session.add(bookmark)
    session.commit()
    session.refresh(bookmark)
    return bookmark