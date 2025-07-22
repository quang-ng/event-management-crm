from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi import BackgroundTasks

from app.routers import email as email_router
from app.utils import email_utils


@pytest_asyncio.fixture
def mock_db():
    table = AsyncMock()
    db = MagicMock()
    db.Table = AsyncMock(return_value=table)
    return db, table

@pytest.mark.asyncio
async def test_send_email_to_filtered_users_success(monkeypatch, mock_db):
    db, table = mock_db
    # Patch user_service.filter_users to return users with emails
    monkeypatch.setattr(email_router.user_service, "filter_users", AsyncMock(return_value={
        "results": [
            {"email": "a@example.com"},
            {"email": "b@example.com"}
        ]
    }))
    # Patch send_email to just record the call
    called = {}
    def fake_send_email(background_tasks, subject, body, emails, db):
        called["emails"] = emails
        called["subject"] = subject
        called["body"] = body
    monkeypatch.setattr(email_router, "send_email", fake_send_email)
    background_tasks = BackgroundTasks()
    response = await email_router.send_email_to_filtered_users(
        background_tasks,
        subject="Test Subject",
        body="Test Body",
        company=None,
        job_title=None,
        city=None,
        state=None,
        events_hosted_min=None,
        events_hosted_max=None,
        events_attended_min=None,
        events_attended_max=None,
        limit=10,
        cursor=None,
        sort_by=None,
        sort_order="asc",
        db=db
    )
    assert response["message"] == "Emails sent to 2 users."
    assert called["emails"] == ["a@example.com", "b@example.com"]
    assert called["subject"] == "Test Subject"
    assert called["body"] == "Test Body"

@pytest.mark.asyncio
async def test_send_email_to_filtered_users_no_users(monkeypatch, mock_db):
    db, table = mock_db
    monkeypatch.setattr(email_router.user_service, "filter_users", AsyncMock(return_value={"results": []}))
    background_tasks = BackgroundTasks()
    response = await email_router.send_email_to_filtered_users(
        background_tasks,
        subject="Test Subject",
        body="Test Body",
        company=None,
        job_title=None,
        city=None,
        state=None,
        events_hosted_min=None,
        events_hosted_max=None,
        events_attended_min=None,
        events_attended_max=None,
        limit=10,
        cursor=None,
        sort_by=None,
        sort_order="asc",
        db=db
    )
    assert response["message"] == "No users found for the given criteria."

@pytest.mark.asyncio
async def test_get_email_logs(monkeypatch, mock_db):
    db, table = mock_db
    table.scan.return_value = {"Items": [{"id": 1, "recipient": "a@example.com"}]}
    monkeypatch.setattr(db, "Table", AsyncMock(return_value=table))
    response = await email_router.get_email_logs(db=db)
    assert "logs" in response
    assert response["logs"] == [{"id": 1, "recipient": "a@example.com"}]
