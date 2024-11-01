from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, HTTPException, Depends, status
from db.models.user import User
from db.db_settings import get_db
from schemas.user_schema import UserCreateSchema, UserSchema, Token, UserUpdateSchema
from sqlalchemy.orm import Session
from utils.auth import get_current_active_user, authenticate_user, create_access_token
from utils.hashing import get_password_hash, verify_password
from utils.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: str, db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/login/", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    user: UserCreateSchema,
    db: Session = Depends(get_db)
):
    exst_usr = db.query(User).filter(User.email == user.email).first()
    form_data = OAuth2PasswordRequestForm(username=exst_usr.username, password=user.password)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/users/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/users/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UserCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    existing_user = db.query(User).filter(User.id == user_id).first()

    if not existing_user or existing_user.id != current_user.id:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, getattr(existing_user, "password")):
        raise HTTPException(status_code=400, detail="Incorrect password")

    for key, value in user.dict(exclude_unset=True).items():
        if key == "password":
            setattr(existing_user, "password", get_password_hash(value))
        else:
            setattr(existing_user, key, value)

    db.commit()
    db.refresh(existing_user)
    return existing_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, user: UserUpdateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user or existing_user.id != user_id:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, getattr(existing_user, "password")):
        raise HTTPException(status_code=400, detail="Incorrect password")

    db.delete(existing_user)
    db.commit()
