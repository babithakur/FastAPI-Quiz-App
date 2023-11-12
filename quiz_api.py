from fastapi import FastAPI, Path
from pymongo import MongoClient

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client.quiz
collection = db.questions

@app.get("/questions/{num}",
         summary="Get computer science quiz questions.",
         response_description="Here's the requested question:"
         )
async def get_questions(num: int = Path(..., gt=0, le=10)):
    """
    This API provides basic computer science quiz questions that can be used to create quiz applications. The API is based on FastAPI.

    - The necessary parameters to be included is num which ranges from 1 to 10.
    - This API returns a question, it's answer options and the correct answer as 'question', 'options' and 'answer' respectively.
    - Any request with the num parameter less than 1 or greater than 10 will be considered invalid.

    Thank you for using this API.
    """
    question = collection.find({}, {'_id':False}).limit(1).skip(num-1)
    for qn in question:
        return qn
