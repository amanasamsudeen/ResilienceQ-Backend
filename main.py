from fastapi import Depends, FastAPI, HTTPException
from routers import auth,chat,personal_info,assessment,ai_recommendation

from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel, EmailStr

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:4321",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(personal_info.router)
app.include_router(assessment.router)
app.include_router(ai_recommendation.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        



