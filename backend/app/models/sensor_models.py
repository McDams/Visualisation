from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class SensorType(str, Enum):
    """Sensor types."""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============= SENSOR SCHEMAS =============

class SensorCreate(BaseModel):
    """Schema for creating a sensor."""
    name: str = Field(..., min_length=1, max_length=255)
    sensor_type: SensorType
    location: Optional[str] = Field(None, max_length=255)
    unit: str = Field(..., max_length=50)
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class SensorUpdate(BaseModel):
    """Schema for updating a sensor."""
    name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    is_active: Optional[bool] = None


class SensorResponse(BaseModel):
    """Schema for sensor response."""
    id: int
    name: str
    sensor_type: SensorType
    location: Optional[str]
    unit: str
    min_value: Optional[float]
    max_value: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= SENSOR READING SCHEMAS =============

class SensorReadingCreate(BaseModel):
    """Schema for creating a sensor reading."""
    sensor_id: int
    value: float


class SensorReadingResponse(BaseModel):
    """Schema for sensor reading response."""
    id: int
    sensor_id: int
    value: float
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SensorData(BaseModel):
    """Legacy schema for sensor data (backward compat)."""
    id: int
    sensor_name: str
    value: float
    timestamp: datetime


# ============= ALERT SCHEMAS =============

class AlertCreate(BaseModel):
    """Schema for creating an alert."""
    sensor_id: int
    alert_type: str = Field(..., max_length=100)
    severity: AlertSeverity = AlertSeverity.MEDIUM
    message: str = Field(..., max_length=500)
    value: Optional[float] = None
    threshold: Optional[float] = None


class AlertResponse(BaseModel):
    """Schema for alert response."""
    id: int
    sensor_id: int
    alert_type: str
    severity: AlertSeverity
    message: str
    value: Optional[float]
    threshold: Optional[float]
    is_resolved: bool
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= HISTORY RESPONSE SCHEMA =============

class HistoryResponse(BaseModel):
    """Schema for paginated history response."""
    page: int
    limit: int
    total: int
    items: list[SensorReadingResponse]


class SensorLatestResponse(BaseModel):
    """Schema for latest sensor readings response."""
    temperature: float
    humidity: float
    light: float
    timestamp: datetime
