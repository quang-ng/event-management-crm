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


def _validate_filter_users_inputs(limit: int, sort_by: Optional[str], sort_order: str, cursor: Optional[str]):
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


def _build_filter_expression(filters: Dict[str, Any]):
    from functools import reduce
    conditions = []
    for key, value in filters.items():
        if value is not None:
            if isinstance(value, tuple):
                min_val, max_val = value
                if min_val is not None:
                    conditions.append(Attr(key).gte(min_val))
                if max_val is not None:
                    conditions.append(Attr(key).lte(max_val))
            else:
                conditions.append(Attr(key).eq(value))
    if not conditions:
        return None
    return reduce(lambda a, b: a & b, conditions)


def _get_gsi_query_kwargs(company, job_title, sort_by, sort_order, limit, cursor):
    if company and sort_by == "job_title":
        kwargs = {
            "IndexName": "company-job_title-index",
            "KeyConditionExpression": Key("company").eq(company),
            "ScanIndexForward": (sort_order == "asc"),
            "Limit": limit + 1,
        }
        if cursor:
            kwargs["ExclusiveStartKey"] = {"company": company, "job_title": cursor}
        return kwargs, "job_title"
    elif job_title and sort_by == "company":
        kwargs = {
            "IndexName": "job_title-company-index",
            "KeyConditionExpression": Key("job_title").eq(job_title),
            "ScanIndexForward": (sort_order == "asc"),
            "Limit": limit + 1,
        }
        if cursor:
            kwargs["ExclusiveStartKey"] = {"job_title": job_title, "company": cursor}
        return kwargs, "company"
    return None, None


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
    _validate_filter_users_inputs(limit, sort_by, sort_order, cursor)
    table = await db.Table("users")

    # Try GSI query if possible
    gsi_kwargs, gsi_cursor_field = _get_gsi_query_kwargs(company, job_title, sort_by, sort_order, limit, cursor)
    if gsi_kwargs:
        try:
            response = await table.query(**gsi_kwargs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DynamoDB query error: {str(e)}")
        items = response.get("Items", [])
        last_evaluated_key = response.get("LastEvaluatedKey")
    else:
        # Build filter expression
        filters = {
            "company": company,
            "job_title": job_title,
            "city": city,
            "state": state,
            "events_hosted": (events_hosted_min, events_hosted_max),
            "events_attended": (events_attended_min, events_attended_max),
        }
        filter_expression = _build_filter_expression(filters)
        scan_kwargs = {"Limit": limit + 1}
        if filter_expression is not None:
            scan_kwargs["FilterExpression"] = filter_expression
        if cursor:
            scan_kwargs["ExclusiveStartKey"] = {"id": int(cursor)}
        response = await table.scan(**scan_kwargs)
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

    # Pagination
    next_cursor = None
    if last_evaluated_key:
        if gsi_cursor_field and last_evaluated_key.get(gsi_cursor_field):
            next_cursor = last_evaluated_key[gsi_cursor_field]
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
