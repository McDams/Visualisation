"""
Sensors service - handles sensor operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from app.models.db_models import Sensor, SensorReading, SensorType
from app.models.sensor_models import SensorCreate, SensorResponse, SensorReadingCreate, SensorLatestResponse
from typing import Optional, List


class SensorService:
    """Service for managing sensors and readings."""
    
    @staticmethod
    def create_sensor(db: Session, sensor: SensorCreate) -> Sensor:
        """Create a new sensor."""
        db_sensor = Sensor(
            name=sensor.name,
            sensor_type=sensor.sensor_type,
            location=sensor.location,
            unit=sensor.unit,
            min_value=sensor.min_value,
            max_value=sensor.max_value
        )
        db.add(db_sensor)
        db.commit()
        db.refresh(db_sensor)
        return db_sensor
    
    @staticmethod
    def get_sensor(db: Session, sensor_id: int) -> Optional[Sensor]:
        """Get sensor by ID."""
        return db.query(Sensor).filter(Sensor.id == sensor_id).first()
    
    @staticmethod
    def get_sensor_by_name(db: Session, name: str) -> Optional[Sensor]:
        """Get sensor by name."""
        return db.query(Sensor).filter(Sensor.name == name).first()
    
    @staticmethod
    def get_all_sensors(db: Session, skip: int = 0, limit: int = 100) -> List[Sensor]:
        """Get all sensors with pagination."""
        return db.query(Sensor).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_active_sensors(db: Session) -> List[Sensor]:
        """Get all active sensors."""
        return db.query(Sensor).filter(Sensor.is_active == True).all()
    
    @staticmethod
    def get_latest_readings(db: Session) -> dict:
        """Get latest readings for each sensor type."""
        sensors = SensorService.get_active_sensors(db)
        readings = {}
        
        for sensor_type in [SensorType.TEMPERATURE, SensorType.HUMIDITY, SensorType.LIGHT]:
            latest = db.query(SensorReading).join(Sensor).filter(
                Sensor.sensor_type == sensor_type,
                Sensor.is_active == True
            ).order_by(desc(SensorReading.timestamp)).first()
            
            if latest:
                readings[sensor_type.value] = float(latest.value)
            else:
                readings[sensor_type.value] = None
        
        readings['timestamp'] = datetime.utcnow()
        return readings
    
    @staticmethod
    def add_reading(db: Session, sensor_id: int, value: float) -> SensorReading:
        """Add a new reading for a sensor."""
        reading = SensorReading(sensor_id=sensor_id, value=value)
        db.add(reading)
        db.commit()
        db.refresh(reading)
        return reading
    
    @staticmethod
    def get_sensor_readings(
        db: Session,
        sensor_id: int,
        limit: int = 100
    ) -> List[SensorReading]:
        """Get recent readings for a specific sensor."""
        return db.query(SensorReading).filter(
            SensorReading.sensor_id == sensor_id
        ).order_by(desc(SensorReading.timestamp)).limit(limit).all()


def get_latest_mock():
    """Legacy function for backward compatibility with existing routes."""
    return {
        "temperature": round(__import__('random').uniform(18, 30), 2),
        "humidity": round(__import__('random').uniform(30, 70), 2),
        "light": __import__('random').randint(100, 800),
        "timestamp": datetime.now().isoformat()
    }


def get_sensor_by_id_mock(id: int):
    """Legacy function for backward compatibility."""
    return {
        "id": id,
        "sensor": "temp",
        "value": round(__import__('random').uniform(18, 30), 2),
        "timestamp": datetime.now().isoformat()
    }
