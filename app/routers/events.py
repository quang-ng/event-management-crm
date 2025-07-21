from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import schemas
from app.services import user_service
from app.utils.database import get_db

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, host_id: int, db: Session = Depends(get_db)):
    return user_service.create_event(db, event, host_id)

@router.post("/register", response_model=schemas.EventRegistration)
def register_user(event_id: int, user_id: int, db: Session = Depends(get_db)):
    return user_service.register_user_for_event(db, user_id, event_id)
