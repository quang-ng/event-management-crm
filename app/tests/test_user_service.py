import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.services import user_service

@pytest_asyncio.fixture
def mock_db():
    table = AsyncMock()
    db = MagicMock()
    db.Table = AsyncMock(return_value=table)
    return db, table

@pytest.mark.asyncio
async def test_filter_users_by_company(mock_db):
    db, table = mock_db
    table.query.return_value = {
        'Items': [{
            'id': 1, 'email': 'a@example.com', 'first_name': 'A', 'last_name': 'B', 'role': 'host', 'company': 'Acme', 'job_title': 'Engineer'
        }],
        'LastEvaluatedKey': None
    }
    result = await user_service.filter_users(db, company='Acme', sort_by='job_title')
    assert result['results'][0]['company'] == 'Acme'
    table.query.assert_awaited()

@pytest.mark.asyncio
async def test_filter_users_by_job_title(mock_db):
    db, table = mock_db
    table.query.return_value = {
        'Items': [{
            'id': 2, 'email': 'b@example.com', 'first_name': 'B', 'last_name': 'C', 'role': 'attendee', 'company': 'Beta', 'job_title': 'Manager'
        }],
        'LastEvaluatedKey': None
    }
    result = await user_service.filter_users(db, job_title='Manager', sort_by='company')
    assert result['results'][0]['job_title'] == 'Manager'
    table.query.assert_awaited()

@pytest.mark.asyncio
async def test_filter_users_scan_in_memory_sort(mock_db):
    db, table = mock_db
    table.scan.return_value = {
        'Items': [
            {'id': 3, 'email': 'c@example.com', 'first_name': 'C', 'last_name': 'D', 'role': 'host', 'company': 'Gamma', 'job_title': 'Designer'},
            {'id': 4, 'email': 'd@example.com', 'first_name': 'D', 'last_name': 'E', 'role': 'attendee', 'company': 'Alpha', 'job_title': 'Engineer'}
        ],
        'LastEvaluatedKey': None
    }
    result = await user_service.filter_users(db, city='TestCity', sort_by='company', sort_order='asc')
    assert result['results'][0]['company'] == 'Alpha'
    table.scan.assert_awaited()

@pytest.mark.asyncio
async def test_filter_users_invalid_limit(mock_db):
    db, _ = mock_db
    with pytest.raises(HTTPException) as exc:
        await user_service.filter_users(db, limit=0)
    assert exc.value.status_code == 400
    assert 'Limit must be between' in exc.value.detail

@pytest.mark.asyncio
async def test_filter_users_invalid_sort_by(mock_db):
    db, _ = mock_db
    with pytest.raises(HTTPException) as exc:
        await user_service.filter_users(db, sort_by='notafield')
    assert exc.value.status_code == 400
    assert 'Invalid sort_by field' in exc.value.detail 