"""
Alerts router - handles alert-related endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.alerts_service import AlertService, get_alerts_mock
from app.models.sensor_models import AlertResponse, AlertCreate
from app.models.db_models import AlertSeverity

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[dict])
def get_alerts(
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get recent alerts with fallback to mock data.
    """
    try:
        alerts = AlertService.get_alerts(db, limit=limit)
        return [
            {
                "id": alert.id,
                "type": alert.alert_type,
                "message": alert.message,
                "value": alert.value,
                "severity": alert.severity.value,
                "is_resolved": alert.is_resolved,
                "timestamp": alert.created_at.isoformat()
            }
            for alert in alerts
        ]
    except Exception:
        # Fallback to mock if database fails
        return get_alerts_mock()


@router.get("/active", response_model=list[AlertResponse])
def get_active_alerts(db: Session = Depends(get_db)):
    """Get all unresolved alerts."""
    alerts = AlertService.get_active_alerts(db)
    return alerts


@router.post("", response_model=AlertResponse, status_code=201)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert."""
    from app.services.sensors_service import SensorService
    
    # Verify sensor exists
    sensor = SensorService.get_sensor(db, alert.sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    return AlertService.create_alert(
        db,
        sensor_id=alert.sensor_id,
        alert_type=alert.alert_type,
        message=alert.message,
        severity=alert.severity,
        value=alert.value,
        threshold=alert.threshold
    )


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as resolved."""
    alert = AlertService.resolve_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/check-thresholds")
def check_thresholds(db: Session = Depends(get_db)):
    """
    Check all sensor readings against thresholds and create alerts if needed.
    Useful for scheduled tasks or on-demand checks.
    """
    new_alerts = AlertService.check_thresholds(db)
    return {
        "alerts_created": len(new_alerts),
        "alerts": [
            {
                "id": alert.id,
                "sensor_id": alert.sensor_id,
                "message": alert.message,
                "severity": alert.severity.value
            }
            for alert in new_alerts
        ]
    }
