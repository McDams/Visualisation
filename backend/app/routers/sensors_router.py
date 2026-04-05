"""
Sensors router - handles sensor-related endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.sensors_service import SensorService, get_latest_mock, get_sensor_by_id_mock
from app.models.sensor_models import (
    SensorCreate, 
    SensorResponse, 
    SensorReadingCreate,
    SensorReadingResponse,
    SensorLatestResponse
)

router = APIRouter(prefix="/sensors", tags=["sensors"])


# ============= READ ENDPOINTS =============

@router.get("/latest", response_model=dict)
def get_latest(db: Session = Depends(get_db)):
    """
    Get latest readings from all active sensors.
    Falls back to mock data if no real data available.
    """
    try:
        readings = SensorService.get_latest_readings(db)
        return {
            "temperature": readings.get('temperature'),
            "humidity": readings.get('humidity'),
            "light": readings.get('light'),
            "timestamp": readings.get('timestamp').isoformat()
        }
    except Exception:
        # Fallback to mock if database fails
        return get_latest_mock()


@router.get("/by-id/{sensor_id}", response_model=dict)
def get_by_id(sensor_id: int, db: Session = Depends(get_db)):
    """Get a specific sensor by ID."""
    sensor = SensorService.get_sensor(db, sensor_id)
    if not sensor:
        # Fallback to mock
        return get_sensor_by_id_mock(sensor_id)
    
    return {
        "id": sensor.id,
        "name": sensor.name,
        "sensor_type": sensor.sensor_type.value,
        "unit": sensor.unit,
        "is_active": sensor.is_active
    }


@router.get("", response_model=list[SensorResponse])
def list_sensors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all sensors with pagination."""
    sensors = SensorService.get_all_sensors(db, skip=skip, limit=limit)
    return sensors


@router.get("/active", response_model=list[SensorResponse])
def get_active_sensors(db: Session = Depends(get_db)):
    """Get all active sensors."""
    sensors = SensorService.get_active_sensors(db)
    return sensors


# ============= CREATE ENDPOINTS =============

@router.post("", response_model=SensorResponse, status_code=201)
def create_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    """Create a new sensor."""
    existing = SensorService.get_sensor_by_name(db, sensor.name)
    if existing:
        raise HTTPException(status_code=400, detail="Sensor with this name already exists")
    
    return SensorService.create_sensor(db, sensor)


@router.post("/{sensor_id}/readings", response_model=SensorReadingResponse, status_code=201)
def add_reading(
    sensor_id: int,
    reading: SensorReadingCreate,
    db: Session = Depends(get_db)
):
    """Add a new reading for a sensor."""
    sensor = SensorService.get_sensor(db, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    return SensorService.add_reading(db, sensor_id, reading.value)


@router.get("/{sensor_id}/readings", response_model=list[SensorReadingResponse])
def get_sensor_readings(
    sensor_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get recent readings for a specific sensor."""
    sensor = SensorService.get_sensor(db, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    return SensorService.get_sensor_readings(db, sensor_id, limit=limit)
