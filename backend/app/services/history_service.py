"""
History service - handles historical data queries.
"""

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models.db_models import SensorReading, Sensor, SensorType
from app.models.sensor_models import SensorReadingResponse
from typing import List, Optional


class HistoryService:
    """Service for querying historical data."""
    
    @staticmethod
    def get_readings_paginated(
        db: Session,
        page: int = 1,
        limit: int = 20,
        sensor_type: Optional[str] = None,
        days: int = 5,
        sort_by: str = "timestamp"
    ) -> dict:
        """
        Get paginated sensor readings with optional filtering.
        
        Args:
            db: Database session
            page: Page number (1-indexed)
            limit: Items per page
            sensor_type: Filter by sensor type (temperature, humidity, light)
            days: Days of history to retrieve
            sort_by: Sort column (timestamp, value, etc.)
        """
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Base query
        query = db.query(SensorReading).filter(
            SensorReading.timestamp >= start_date,
            SensorReading.timestamp <= end_date
        )
        
        # Filter by sensor type if provided
        if sensor_type:
            query = query.join(Sensor).filter(
                Sensor.sensor_type == sensor_type
            )
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if sort_by == "value":
            query = query.order_by(asc(SensorReading.value))
        else:  # default to timestamp descending
            query = query.order_by(desc(SensorReading.timestamp))
        
        # Apply pagination
        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()
        
        return {
            "page": page,
            "limit": limit,
            "total": total,
            "items": [
                {
                    "id": item.id,
                    "sensor_id": item.sensor_id,
                    "value": float(item.value),
                    "timestamp": item.timestamp,
                    "created_at": item.created_at
                }
                for item in items
            ]
        }
    
    @staticmethod
    def get_sensor_statistics(
        db: Session,
        sensor_id: int,
        days: int = 7
    ) -> dict:
        """Get statistics for a specific sensor."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        readings = db.query(SensorReading).filter(
            SensorReading.sensor_id == sensor_id,
            SensorReading.timestamp >= start_date
        ).all()
        
        if not readings:
            return {
                "sensor_id": sensor_id,
                "count": 0,
                "average": None,
                "min": None,
                "max": None
            }
        
        values = [float(r.value) for r in readings]
        
        return {
            "sensor_id": sensor_id,
            "count": len(values),
            "average": round(sum(values) / len(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "latest": float(readings[-1].value),
            "latest_timestamp": readings[-1].timestamp
        }


def generate_mock_history():
    """Legacy function for backward compatibility."""
    sensors = ["temp", "humidity", "light"]
    history = []
    now = datetime.now()

    for day_offset in range(5):
        day = now - timedelta(days=day_offset)

        for hour in range(0, 24, 3):
            timestamp = day.replace(hour=hour, minute=0, second=0, microsecond=0)

            entry = {
                "timestamp": timestamp.isoformat(),
                "sensor": random.choice(sensors),
                "value": round(random.uniform(10, 35), 2)
            }

            history.append(entry)

    history = sorted(history, key=lambda x: x["timestamp"])
    return history


def get_history_mock(page, limit, sensor, sort_by):
    """Legacy function for backward compatibility."""
    data = generate_mock_history()

    if sensor:
        data = [d for d in data if d["sensor"] == sensor]

    data = sorted(data, key=lambda x: x[sort_by])

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": len(data),
        "items": data[start:end]
    }
