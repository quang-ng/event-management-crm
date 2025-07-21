from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services import analytics_service
from app.utils.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/event_attendance/{event_id}")
def event_attendance(event_id: int, db: Session = Depends(get_db)):
    return {"attendance": analytics_service.get_event_attendance(db, event_id)}

@router.get("/user_engagement/{user_id}")
def user_engagement(user_id: int, db: Session = Depends(get_db)):
    return {"engagement": analytics_service.get_user_engagement(db, user_id)}
