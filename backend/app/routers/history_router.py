"""
History router - handles historical data queries.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.history_service import HistoryService, get_history_mock
from app.models.sensor_models import HistoryResponse

router = APIRouter(prefix="/sensors", tags=["history"])


@router.get("/history", response_model=dict)
def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=1000),
    sensor_type: Optional[str] = Query(None, description="Filter by sensor type (temperature, humidity, light)"),
    days: int = Query(5, ge=1, le=365, description="Days of history to retrieve"),
    sort_by: Optional[str] = Query("timestamp", regex="^(timestamp|value)$"),
    db: Session = Depends(get_db)
):
    """
    Get paginated historical sensor readings with optional filtering.
    
    Parameters:
    - page: Page number (1-indexed)
    - limit: Items per page (max 1000)
    - sensor_type: Filter by sensor type (temperature, humidity, light)
    - days: Number of days of history to retrieve (1-365)
    - sort_by: Sort by timestamp or value
    """
    try:
        return HistoryService.get_readings_paginated(
            db,
            page=page,
            limit=limit,
            sensor_type=sensor_type,
            days=days,
            sort_by=sort_by
        )
    except Exception:
        # Fallback to mock if database fails
        return get_history_mock(page, limit, sensor_type, sort_by)


@router.get("/statistics/{sensor_id}", response_model=dict)
def get_sensor_statistics(
    sensor_id: int,
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific sensor over a time period.
    
    Returns: count, average, min, max, latest value, and timestamp.
    """
    return HistoryService.get_sensor_statistics(db, sensor_id, days=days)
