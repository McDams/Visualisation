"""
Measurements router - handles measurement data endpoints.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime

from app.services.measurements_service import MeasurementsService
from app.models.measurement_models import (
    TimeSeriesResponse,
    SensorStatistics,
    ComparisonResponse
)

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.get("/latest")
def get_latest_readings():
    """Get latest readings for all measurement types."""
    try:
        return MeasurementsService.get_latest_readings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paginated")
def get_measurements_paginated(
    sensor_id: Optional[int] = Query(None),
    measurement_type_id: Optional[int] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(1000, le=10000),
    offset: int = Query(0, ge=0)
):
    """Get paginated measurements with optional filters."""
    try:
        return MeasurementsService.get_measurements_paginated(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeseries", response_model=TimeSeriesResponse)
def get_time_series(
    sensor_id: Optional[int] = Query(None),
    measurement_type_id: Optional[int] = Query(None),
    days: int = Query(7, ge=1, le=365)
):
    """Get time series data for visualization."""
    try:
        return MeasurementsService.get_time_series(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            days=days
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare", response_model=ComparisonResponse)
def compare_sensors(
    measurement_type_id: int = Query(...),
    sensor_ids: Optional[str] = Query(None, description="Comma-separated sensor IDs"),
    days: int = Query(7, ge=1, le=365)
):
    """Compare multiple sensors for same measurement type."""
    try:
        sensor_id_list = None
        if sensor_ids:
            sensor_id_list = [int(sid.strip()) for sid in sensor_ids.split(',')]
        
        return MeasurementsService.compare_sensors(
            measurement_type_id=measurement_type_id,
            sensor_ids=sensor_id_list,
            days=days
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid sensor IDs: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/{sensor_id}", response_model=SensorStatistics)
def get_sensor_statistics(
    sensor_id: int,
    measurement_type_id: Optional[int] = Query(None),
    days: int = Query(7, ge=1, le=365)
):
    """Get detailed statistics for a sensor."""
    try:
        return MeasurementsService.get_sensor_statistics(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            days=days
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
