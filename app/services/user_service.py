# User CRUD and event registration logic
from typing import List

from sqlalchemy.orm import Session

from app.models import models
from app.schemas import schemas


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_event(db: Session, event: schemas.EventCreate, host_id: int):
    db_event = models.Event(**event.dict(), host_id=host_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def register_user_for_event(db: Session, user_id: int, event_id: int):
    registration = models.EventRegistration(user_id=user_id, event_id=event_id)
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration
