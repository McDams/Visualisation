"""
Statistics router - handles advanced statistical analysis endpoints.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.services.stats_service import StatsService
from app.models.measurement_models import (
    DistributionResponse,
    CorrelationResponse,
    DashboardOverview
)

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview():
    """Get dashboard overview with key metrics."""
    try:
        return StatsService.get_dashboard_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/distribution", response_model=DistributionResponse)
def get_distribution(
    measurement_type_id: int = Query(...),
    sensor_id: Optional[int] = Query(None),
    days: int = Query(7, ge=1, le=365),
    bins: int = Query(10, ge=5, le=50)
):
    """Get distribution (histogram) for measurement data."""
    try:
        return StatsService.get_distribution(
            measurement_type_id=measurement_type_id,
            sensor_id=sensor_id,
            days=days,
            bins=bins
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/correlation", response_model=CorrelationResponse)
def get_correlation(
    measurement_type_id: int = Query(...),
    sensor1_id: int = Query(...),
    sensor2_id: int = Query(...),
    days: int = Query(7, ge=1, le=365)
):
    """Calculate correlation between two sensors."""
    try:
        return StatsService.get_correlation(
            measurement_type_id=measurement_type_id,
            sensor1_id=sensor1_id,
            sensor2_id=sensor2_id,
            days=days
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies/{sensor_id}")
def detect_anomalies(
    sensor_id: int,
    measurement_type_id: int = Query(...),
    days: int = Query(7, ge=1, le=365),
    threshold: float = Query(2.0, ge=1.0, le=5.0)
):
    """Detect anomalies in sensor data using z-score method."""
    try:
        return StatsService.detect_anomalies(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            days=days,
            threshold=threshold
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend/{sensor_id}")
def get_trend(
    sensor_id: int,
    measurement_type_id: int = Query(...),
    days: int = Query(7, ge=1, le=365)
):
    """Analyze trend (increasing/decreasing/stable) for a sensor."""
    try:
        return StatsService.get_trend_analysis(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            days=days
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
