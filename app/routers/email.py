
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Query
from sqlalchemy.orm import Session

from app.models import models
from app.services import user_service
from app.utils.database import get_db
from app.utils.email_utils import send_email

router = APIRouter(prefix="/email", tags=["email"])


@router.post("/send-to-filtered-users")
async def send_email_to_filtered_users(
    background_tasks: BackgroundTasks,
    subject: str = Body(..., embed=True),
    body: str = Body(..., embed=True),
    company: Optional[str] = None,
    job_title: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    events_hosted_min: Optional[int] = None,
    events_hosted_max: Optional[int] = None,
    events_attended_min: Optional[int] = None,
    events_attended_max: Optional[int] = None,
    limit: int = Query(100, ge=1, le=200),
    cursor: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    db = Depends(get_db),
):
    """
    Send emails to users matching filter criteria (same as /users/filter).
    """
    result = await user_service.filter_users(
        db,
        company=company,
        job_title=job_title,
        city=city,
        state=state,
        events_hosted_min=events_hosted_min,
        events_hosted_max=events_hosted_max,
        events_attended_min=events_attended_min,
        events_attended_max=events_attended_max,
        limit=limit,
        cursor=cursor,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    emails = [user.get("email") for user in result["results"] if user.get("email")]
    if not emails:
        return {"message": "No users found for the given criteria."}
    send_email(background_tasks, subject, body, emails, db)
    return {"message": f"Emails sent to {len(emails)} users."}



@router.get("/logs", summary="Get all email logs")
async def get_email_logs(db = Depends(get_db)):
    """
    Retrieve all email logs from the email_logs table.
    """
    table = await db.Table("email_logs")
    response = await table.scan()

    items = response.get("Items", [])
    return {"logs": items}