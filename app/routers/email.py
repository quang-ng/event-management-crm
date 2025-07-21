from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.models import models
from app.utils.database import get_db
from app.utils.email_utils import send_email

router = APIRouter(prefix="/email", tags=["email"])

@router.post("/send")
def send_email_to_users(background_tasks: BackgroundTasks, subject: str, body: str, role: str = None, db: Session = Depends(get_db)):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    recipients = [user.email for user in query.all()]
    send_email(background_tasks, subject, body, recipients)
    return {"message": f"Emails sent to {len(recipients)} users."}
