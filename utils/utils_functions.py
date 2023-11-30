from config.db import users_collection
from config.auth import *
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from models.model import TokenData

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy() #copying data so that it won't  affect original data
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    fetch_db_user = users_collection.find_one({f"{username}.username": username})
    if fetch_db_user:
        hashed_password = fetch_db_user[f"{username}"]["password"] #returns password
        verify_password = pwd_context.verify(password, hashed_password)
        if verify_password:
            return fetch_db_user
    return False

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials!", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    user = users_collection.find_one({f"{token_data.username}.username": token_data.username})
    if user == 'null':
        raise credential_exception
    return user[f"{username}"]
