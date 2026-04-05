"""
Alerts service - handles alert operations.
"""

import random
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.db_models import Alert, AlertSeverity, Sensor, SensorReading, SensorType
from typing import List, Optional


class AlertService:
    """Service for managing alerts."""
    
    @staticmethod
    def create_alert(
        db: Session,
        sensor_id: int,
        alert_type: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        value: Optional[float] = None,
        threshold: Optional[float] = None
    ) -> Alert:
        """Create a new alert."""
        alert = Alert(
            sensor_id=sensor_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            value=value,
            threshold=threshold
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def get_active_alerts(db: Session) -> List[Alert]:
        """Get all unresolved alerts."""
        return db.query(Alert).filter(
            Alert.is_resolved == False
        ).order_by(desc(Alert.created_at)).all()
    
    @staticmethod
    def get_alerts(db: Session, limit: int = 50) -> List[Alert]:
        """Get recent alerts."""
        return db.query(Alert).order_by(
            desc(Alert.created_at)
        ).limit(limit).all()
    
    @staticmethod
    def resolve_alert(db: Session, alert_id: int) -> Optional[Alert]:
        """Mark an alert as resolved."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)
        return alert
    
    @staticmethod
    def check_thresholds(db: Session) -> List[Alert]:
        """
        Check sensor readings against thresholds and create alerts if needed.
        Returns newly created alerts.
        """
        new_alerts = []
        sensors = db.query(Sensor).filter(Sensor.is_active == True).all()
        
        for sensor in sensors:
            latest_reading = db.query(SensorReading).filter(
                SensorReading.sensor_id == sensor.id
            ).order_by(desc(SensorReading.timestamp)).first()
            
            if not latest_reading:
                continue
            
            value = latest_reading.value
            
            # Check min threshold
            if sensor.min_value and value < sensor.min_value:
                alert = AlertService.create_alert(
                    db,
                    sensor_id=sensor.id,
                    alert_type="threshold_exceeded",
                    message=f"{sensor.name} below minimum threshold ({sensor.min_value})",
                    severity=AlertSeverity.HIGH,
                    value=value,
                    threshold=sensor.min_value
                )
                new_alerts.append(alert)
            
            # Check max threshold
            if sensor.max_value and value > sensor.max_value:
                alert = AlertService.create_alert(
                    db,
                    sensor_id=sensor.id,
                    alert_type="threshold_exceeded",
                    message=f"{sensor.name} above maximum threshold ({sensor.max_value})",
                    severity=AlertSeverity.CRITICAL,
                    value=value,
                    threshold=sensor.max_value
                )
                new_alerts.append(alert)
        
        return new_alerts


def get_alerts_mock():
    """Legacy function for backward compatibility."""
    alerts = [
        {"type": "temp", "message": "Température élevée", "value": 32},
        {"type": "humidity", "message": "Humidité basse", "value": 25},
        {"type": "light", "message": "Luminosité anormale", "value": 900},
    ]

    if random.random() < 0.5:
        return []

    return random.sample(alerts, random.randint(1, 3))
