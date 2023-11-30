from fastapi import Path, FastAPI, Depends, HTTPException, status, APIRouter
from config.db import users_collection, quiz_collection
from config.auth import *
from models.model import *
from utils.utils_functions import *

quiz = APIRouter()

@quiz.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password.", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user[f"{form_data.username}"]["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@quiz.post("/signup", summary="Sign up to quiz API")
async def user_signup(user: UserSignup):
    user.password = get_password_hash(user.password)
    user_data = dict(user)
    db_user_data = {user_data["username"]: user_data}
    user_id = users_collection.insert_one(db_user_data).inserted_id
    return {"success": f"You are signed up with user id: {user_id}"}

@quiz.get("/questions/{num}",
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


