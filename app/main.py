
import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routers import analytics, email, events, users
from app.utils.dynamodb_init import register_dynamodb_init

app = FastAPI()

register_dynamodb_init(app)

app.include_router(users.router)
app.include_router(events.router)
app.include_router(analytics.router)
app.include_router(email.router)

@app.get("/")
def root():
    return {"message": "Event Management CRM API"}
