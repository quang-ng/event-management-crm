from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from boto3.dynamodb.conditions import Attr, Key

# Allowed fields for sorting and filtering
USER_SORTABLE_FIELDS = {
    "id",
    "first_name",
    "last_name",
    "email",
    "company",
    "job_title",
    "city",
    "state",
    "events_hosted",
    "events_attended",
}


async def filter_users(
    db,
    company: Optional[str] = None,
    job_title: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    events_hosted_min: Optional[int] = None,
    events_hosted_max: Optional[int] = None,
    events_attended_min: Optional[int] = None,
    events_attended_max: Optional[int] = None,
    limit: int = 100,
    cursor: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
) -> Dict[str, Any]:
    """
    Filter users from DynamoDB with async scan or query, in-memory sort if needed, and pagination.
    Uses GSIs for efficient company/job_title sorting.
    Raises HTTPException for invalid input.
    """
    # --- Input Validation ---
    if limit < 1 or limit > 200:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 200.")
    if sort_by and sort_by not in USER_SORTABLE_FIELDS:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by field: {sort_by}")
    if sort_order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=400, detail="sort_order must be 'asc' or 'desc'."
        )
    try:
        if cursor is not None:
            cursor_val = int(cursor)
            if cursor_val < 0:
                raise ValueError
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid cursor value.")
    table = db.Table("users")
    items = []
    last_evaluated_key = None
    # --- Use GSI for efficient query if possible ---
    if company and sort_by == "job_title":
        # Query using company-job_title-index
        query_kwargs = {
            "IndexName": "company-job_title-index",
            "KeyConditionExpression": Key("company").eq(company),
            "ScanIndexForward": (sort_order == "asc"),
            "Limit": limit + 1,
        }
        if cursor:
            query_kwargs["ExclusiveStartKey"] = {
                "company": company,
                "job_title": cursor,
            }
        try:
            response = await table.query(**query_kwargs)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"DynamoDB query error: {str(e)}"
            )
        items = response.get("Items", [])
        last_evaluated_key = response.get("LastEvaluatedKey")
    elif job_title and sort_by == "company":
        # Query using job_title-company-index
        query_kwargs = {
            "IndexName": "job_title-company-index",
            "KeyConditionExpression": Key("job_title").eq(job_title),
            "ScanIndexForward": (sort_order == "asc"),
            "Limit": limit + 1,
        }
        if cursor:
            query_kwargs["ExclusiveStartKey"] = {
                "job_title": job_title,
                "company": cursor,
            }
        try:
            response = await table.query(**query_kwargs)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"DynamoDB query error: {str(e)}"
            )
        items = response.get("Items", [])
        last_evaluated_key = response.get("LastEvaluatedKey")
    else:
        # --- Fallback: Scan with filters and in-memory sort ---
        filter_expression = None
        if company:
            filter_expression = (
                Attr("company").eq(company)
                if not filter_expression
                else filter_expression & Attr("company").eq(company)
            )
        if job_title:
            filter_expression = (
                Attr("job_title").eq(job_title)
                if not filter_expression
                else filter_expression & Attr("job_title").eq(job_title)
            )
        if city:
            filter_expression = (
                Attr("city").eq(city)
                if not filter_expression
                else filter_expression & Attr("city").eq(city)
            )
        if state:
            filter_expression = (
                Attr("state").eq(state)
                if not filter_expression
                else filter_expression & Attr("state").eq(state)
            )
        if events_hosted_min is not None:
            filter_expression = (
                Attr("events_hosted").gte(events_hosted_min)
                if not filter_expression
                else filter_expression & Attr("events_hosted").gte(events_hosted_min)
            )
        if events_hosted_max is not None:
            filter_expression = (
                Attr("events_hosted").lte(events_hosted_max)
                if not filter_expression
                else filter_expression & Attr("events_hosted").lte(events_hosted_max)
            )
        if events_attended_min is not None:
            filter_expression = (
                Attr("events_attended").gte(events_attended_min)
                if not filter_expression
                else filter_expression
                & Attr("events_attended").gte(events_attended_min)
            )
        if events_attended_max is not None:
            filter_expression = (
                Attr("events_attended").lte(events_attended_max)
                if not filter_expression
                else filter_expression
                & Attr("events_attended").lte(events_attended_max)
            )
        scan_kwargs = {"Limit": limit + 1}
        if filter_expression is not None:
            scan_kwargs["FilterExpression"] = filter_expression
        if cursor:
            scan_kwargs["ExclusiveStartKey"] = {"id": int(cursor)}
        # try:
        response = await table.scan(**scan_kwargs)
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=500, detail=f"DynamoDB scan error: {str(e)}"
        #     )
        items = response.get("Items", [])
        last_evaluated_key = response.get("LastEvaluatedKey")
        # In-memory sort if requested
        if sort_by:
            try:
                items = sorted(
                    items, key=lambda x: x.get(sort_by), reverse=(sort_order == "desc")
                )
            except Exception:
                raise HTTPException(status_code=500, detail="Error sorting results.")
    # --- Pagination ---
    next_cursor = None
    if last_evaluated_key:
        # For GSI queries, use the sort key as the cursor
        if company and sort_by == "job_title" and last_evaluated_key.get("job_title"):
            next_cursor = last_evaluated_key["job_title"]
        elif job_title and sort_by == "company" and last_evaluated_key.get("company"):
            next_cursor = last_evaluated_key["company"]
        elif last_evaluated_key.get("id"):
            next_cursor = str(last_evaluated_key["id"])
    results = items[:limit]
    return {
        "limit": limit,
        "cursor": cursor,
        "next_cursor": next_cursor,
        "count": len(results),
        "results": results,
    }
