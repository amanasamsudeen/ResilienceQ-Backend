from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from auth.dependencies import get_current_user
from schemas.user_schema import UserRegister, UserLogin, UserUpdate
from security.password import hash_password, verify_password
from services.jwt_handler import create_access_token
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from dotenv import load_dotenv;

import os;
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/register", status_code=201)
def register_user(user: UserRegister, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hash_password(user.password),
        institution=user.institution
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

   
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": str(db_user.user_id), "role": db_user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful"
    }


# ------------------ GET CURRENT USER ------------------
@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.user_id,
        "name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "institution": current_user.institution
    }
    
@router.put("/update")
def update_user(
    user_data: UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch user
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    user.full_name = user_data.name
    user.email = user_data.email
    user.institution = user_data.institution

    db.commit()
    db.refresh(user)

    return {
        "id": user.user_id,
        "name": user.full_name,
        "email": user.email,
        "role": user.role,
        "institution": user.institution
    }