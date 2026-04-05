"""
Data models for sensor system (Pydantic schemas).
Corresponds to PostgreSQL table structure.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any


# ============= SENSOR MODELS =============

class SensorBase(BaseModel):
    """Base sensor model."""
    id: int
    eui64: str = Field(..., alias="EUI64")
    name: str
    reservoir: Optional[str] = None
    active: bool = True
    metadata: Optional[dict] = None
    display_order: int = 0


class SensorResponse(SensorBase):
    """Sensor response model."""
    
    class Config:
        from_attributes = True


# ============= MEASUREMENT TYPE MODELS =============

class MeasurementTypeBase(BaseModel):
    """Base measurement type model."""
    id: int
    code: str
    unit: str
    value_domain: str
    description: Optional[str] = None


class MeasurementTypeResponse(MeasurementTypeBase):
    """Measurement type response model."""
    
    class Config:
        from_attributes = True


# ============= STATISTICS DIMENSION MODELS =============

class StatisticDimensionBase(BaseModel):
    """Base statistic dimension model."""
    id: int
    code: str
    description: Optional[str] = None


class StatisticDimensionResponse(StatisticDimensionBase):
    """Statistic dimension response model."""
    
    class Config:
        from_attributes = True


# ============= MEASUREMENT MODELS =============

class MeasurementBase(BaseModel):
    """Base measurement model."""
    time: datetime
    sensor_id: int
    measurement_type_id: int
    statistic_id: Optional[int] = None
    value_num: float
    internal_count: int = 1


class MeasurementResponse(MeasurementBase):
    """Measurement response model."""
    sensor_name: Optional[str] = None
    measurement_type_code: Optional[str] = None
    measurement_type_unit: Optional[str] = None
    statistic_code: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============= AGGREGATED MODELS =============

class SensorWithLatestReading(SensorResponse):
    """Sensor with latest reading."""
    latest_reading: Optional[MeasurementResponse] = None


class SensorStatistics(BaseModel):
    """Sensor statistics model."""
    sensor_id: int
    sensor_name: Optional[str] = None
    measurement_type_code: Optional[str] = None
    count: int = 0
    min: Optional[float] = None
    max: Optional[float] = None
    avg: Optional[float] = None
    latest: Optional[float] = None
    measurements: List[MeasurementResponse] = []


class DashboardOverview(BaseModel):
    """Dashboard overview model."""
    timestamp: datetime
    sensors_count: int
    active_sensors: int
    measurements_count: int
    latest_readings: dict[str, Optional[float]]  # {sensor_name: value}


# ============= FILTER & QUERY MODELS =============

class MeasurementFilter(BaseModel):
    """Measurement filter model."""
    sensor_id: Optional[int] = None
    measurement_type_id: Optional[int] = None
    statistic_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(1000, le=10000)
    offset: int = Field(0, ge=0)


class TimeSeriesDataPoint(BaseModel):
    """Time series data point."""
    time: datetime
    value: float
    sensor_name: str
    measurement_type: str
    unit: str


class TimeSeriesResponse(BaseModel):
    """Time series response."""
    title: str
    unit: str
    data_points: List[TimeSeriesDataPoint]
    count: int


class ComparisonResponse(BaseModel):
    """Comparison response."""
    title: str
    series: dict[str, List[TimeSeriesDataPoint]]  # {sensor_name: data_points}


class DistributionResponse(BaseModel):
    """Distribution response."""
    title: str
    unit: str
    bins: List[int]  # Histogram bins
    labels: List[str]  # Bin labels
    count: int


class CorrelationResponse(BaseModel):
    """Correlation response."""
    title: str
    sensor1: str
    sensor2: str
    correlation: float  # -1 to 1
    data_points_count: int
