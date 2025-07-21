from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
# New endpoint for advanced user filtering
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.schemas import schemas
from app.services import user_service
from app.utils.database import get_db
from builtins import anext  # Add this import for anext

router = APIRouter(prefix="/users", tags=["users"])


# Response schema for filter endpoint
class UserFilterResponse(BaseModel):
    results: List[schemas.User]
    next_cursor: Optional[str]
    count: int


@router.get("/filter", response_model=UserFilterResponse)
async def filter_users(
    company: Optional[str] = None,
    job_title: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    events_hosted_min: Optional[int] = None,
    events_hosted_max: Optional[int] = None,
    events_attended_min: Optional[int] = None,
    events_attended_max: Optional[int] = None,
    limit: int = Query(100, ge=1, le=200, description="Max results per page (1-200)"),
    cursor: Optional[str] = Query(
        None, description="Pagination cursor (user id, company, or job_title depending on sort/filter)"
    ),
    sort_by: Optional[str] = Query(
        None,
        description="Sort by 'company' or 'job_title' for fast server-side sort, or other fields for slower in-memory sort.",
    ),
    sort_order: Optional[str] = Query("asc", description="Sort order: 'asc' or 'desc'"),
    db = Depends(get_db),
):
    """
    Filter and paginate users. For best performance, use:
    - sort_by='job_title' with company filter (server-side sort)
    - sort_by='company' with job_title filter (server-side sort)
    Other sorts/filters are supported but may be slower (in-memory sort).
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
    return result
