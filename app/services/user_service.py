# User CRUD and event registration logic using DynamoDB
import uuid

from app.models import models
from app.schemas import schemas

USERS_TABLE = models.User.__tablename__
EVENTS_TABLE = models.Event.__tablename__
REGISTRATIONS_TABLE = models.EventRegistration.__tablename__

def create_user(db, user: schemas.UserCreate):
    table = db.Table(USERS_TABLE)
    user_id = str(uuid.uuid4())
    item = {"id": user_id, **user.dict()}
    table.put_item(Item=item)
    return item

def get_user(db, user_id: str):
    table = db.Table(USERS_TABLE)
    response = table.get_item(Key={"id": user_id})
    return response.get("Item")

def get_users(db, skip: int = 0, limit: int = 100):
    table = db.Table(USERS_TABLE)
    response = table.scan()
    items = response.get("Items", [])
    return items[skip:skip+limit]

def create_event(db, event: schemas.EventCreate, host_id: str):
    table = db.Table(EVENTS_TABLE)
    event_id = str(uuid.uuid4())
    item = {"id": event_id, **event.dict(), "host_id": host_id}
    table.put_item(Item=item)
    return item

def register_user_for_event(db, user_id: str, event_id: str):
    table = db.Table(REGISTRATIONS_TABLE)
    registration_id = str(uuid.uuid4())
    item = {"id": registration_id, "user_id": user_id, "event_id": event_id}
    table.put_item(Item=item)
    return item
