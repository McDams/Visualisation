"""
Database models for sensors, readings, and alerts.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class SensorType(str, enum.Enum):
    """Enum for sensor types."""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"


class AlertSeverity(str, enum.Enum):
    """Enum for alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Sensor(Base):
    """Sensor device model."""
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    sensor_type = Column(SQLEnum(SensorType), nullable=False)
    location = Column(String(255), nullable=True)
    unit = Column(String(50), nullable=False)  # e.g., "°C", "%", "lux"
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="sensor", cascade="all, delete-orphan")


class SensorReading(Base):
    """Individual sensor reading/measurement."""
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sensor = relationship("Sensor", back_populates="readings")


class Alert(Base):
    """Alert/notification model."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False)  # e.g., "threshold_exceeded"
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.MEDIUM)
    message = Column(String(500), nullable=False)
    value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    sensor = relationship("Sensor", back_populates="alerts")
