# Event analytics and user engagement queries
from typing import List

from sqlalchemy.orm import Session

from app.models import models


def get_event_attendance(db: Session, event_id: int) -> int:
    return db.query(models.EventRegistration).filter(models.EventRegistration.event_id == event_id).count()

def get_user_engagement(db: Session, user_id: int) -> int:
    return db.query(models.EventRegistration).filter(models.EventRegistration.user_id == user_id).count()
