from fastapi import FastAPI
from routes.route import quiz

app = FastAPI()
app.include_router(quiz)
