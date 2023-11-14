from fastapi import Path, FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
import secrets

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class User(BaseModel):
    username: str
    email: str
    full_name: str

class UserSignup(User):
    password: str

class UserInDB(User):
    hashed_password: str

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
quiz_db = client.quiz
quiz_collection = quiz_db.questions
users_collection = quiz_db.users

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

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

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password.", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user[f"{form_data.username}"]["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup", summary="Sign up to quiz API")
async def user_signup(user: UserSignup):
    user.password = get_password_hash(user.password)
    user_data = dict(user)
    db_user_data = {user_data["username"]: user_data}
    user_id = users_collection.insert_one(db_user_data).inserted_id
    return {"success": f"You are signed up with user id: {user_id}"}

@app.get("/questions/{num}",
         summary="Get computer science quiz questions.",
         response_description="Here's the requested question:",
         dependencies = [Depends(get_current_user)]
         )
async def get_questions(num: int = Path(..., gt=0, le=10)):
    """
    This API provides basic computer science quiz questions that can be used to create quiz applications. The API is based on FastAPI.

    - The necessary parameters to be included is num which ranges from 1 to 10.
    - This API returns a question, it's answer options and the correct answer as 'question', 'options' and 'answer' respectively.
    - Any request with the num parameter less than 1 or greater than 10 will be considered invalid.

    Thank you for using this API.
    """
    question = quiz_collection.find({}, {'_id':False}).limit(1).skip(num-1)
    for qn in question:
        return qn
