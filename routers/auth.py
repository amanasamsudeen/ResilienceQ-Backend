from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.email import send_reset_email, send_verification_email
from database import SessionLocal
from models.user import User
from auth.dependencies import get_current_user
from schemas.user_schema import ForgotPasswordRequest, ResetPasswordRequest, UserRegister, UserLogin, UserUpdate
from security.password import hash_password, verify_password
from services.jwt_handler import create_access_token
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from dotenv import load_dotenv;
from passlib.context import CryptContext
import os

from utils.token import ALGORITHM, create_email_token, create_reset_token, verify_email_token;
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()



@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister, db: Session = Depends(get_db)):

    # 🔍 Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # 🔐 Create new user
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hash_password(user.password),
        institution=user.institution,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 🎟 Generate email verification token
    token = create_email_token(new_user.email)

    # 📧 Send verification email
    await send_verification_email(
    email=user.email,
    username=user.full_name,
    token=token
)

    return {
        "message": "User registered successfully. Please verify your email to activate your account."
    }
    
@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

   
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not db_user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in."
        )

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
    
    
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):

    email = verify_email_token(token)

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.commit()

    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_reset_token(user.email)

    reset_link = f"http://localhost:4321/reset-password?token={token}"

    send_reset_email(user.email, reset_link)

    return {"message": "Reset link sent"}

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = pwd_context.hash(data.password)
    user.password_hash = hashed_password
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Password updated"}