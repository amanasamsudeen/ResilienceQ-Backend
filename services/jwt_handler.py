from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "70c00b8f748d75bd54e3d40ba4bf103cee415ddaaaae1948cba2a2370f4c9740"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
