"""
Measurements service - handles measurement data operations.
Uses repository abstraction for CSV or PostgreSQL sources.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from backend.storage import get_repository
from app.models.measurement_models import (
    MeasurementResponse,
    TimeSeriesResponse,
    TimeSeriesDataPoint,
    SensorStatistics,
    ComparisonResponse
)


class MeasurementsService:
    """Service for measurement operations."""
    
    @staticmethod
    def get_measurements_paginated(
        sensor_id: Optional[int] = None,
        measurement_type_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> dict:
        """Get paginated measurements."""
        repo = get_repository()
        
        measurements = repo.get_measurements(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit + offset  # Account for offset
        )
        
        # Apply offset on already sorted data
        paginated = measurements[offset:offset + limit]
        
        return {
            "count": len(paginated),
            "total": len(measurements),
            "offset": offset,
            "limit": limit,
            "measurements": paginated
        }
    
    @staticmethod
    def get_time_series(
        sensor_id: Optional[int] = None,
        measurement_type_id: Optional[int] = None,
        days: int = 7
    ) -> TimeSeriesResponse:
        """Get time series data for visualization."""
        repo = get_repository()
        
        start_time = datetime.utcnow() - timedelta(days=days)
        measurements = repo.get_measurements(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            start_time=start_time
        )
        
        # Enrich with sensor and type info
        sensors = {s['id']: s for s in repo.get_sensors()}
        types = {t['id']: t for t in repo.get_measurement_types()}
        
        data_points = []
        for m in measurements:
            sensor = sensors.get(m['sensor_id'], {})
            mtype = types.get(m['measurement_type_id'], {})
            
            data_points.append(TimeSeriesDataPoint(
                time=datetime.fromisoformat(m['time']),
                value=m['value_num'],
                sensor_name=sensor.get('name', f"Sensor {m['sensor_id']}"),
                measurement_type=mtype.get('code', 'Unknown'),
                unit=mtype.get('unit', '')
            ))
        
        title = f"Time Series: {days} days"
        if sensor_id:
            sensor = sensors.get(sensor_id, {})
            title += f" ({sensor.get('name', 'Unknown')})"
        
        return TimeSeriesResponse(
            title=title,
            unit=types.get(measurement_type_id, {}).get('unit', ''),
            data_points=data_points,
            count=len(data_points)
        )
    
    @staticmethod
    def compare_sensors(
        measurement_type_id: int,
        sensor_ids: Optional[List[int]] = None,
        days: int = 7
    ) -> ComparisonResponse:
        """Compare multiple sensors for same measurement type."""
        repo = get_repository()
        
        # Get all sensor data
        sensors = repo.get_sensors()
        if sensor_ids:
            sensors = [s for s in sensors if s['id'] in sensor_ids]
        
        types = {t['id']: t for t in repo.get_measurement_types()}
        mtype = types.get(measurement_type_id, {})
        
        start_time = datetime.utcnow() - timedelta(days=days)
        
        series = {}
        for sensor in sensors:
            measurements = repo.get_measurements(
                sensor_id=sensor['id'],
                measurement_type_id=measurement_type_id,
                start_time=start_time
            )
            
            data_points = [
                TimeSeriesDataPoint(
                    time=datetime.fromisoformat(m['time']),
                    value=m['value_num'],
                    sensor_name=sensor['name'],
                    measurement_type=mtype.get('code', ''),
                    unit=mtype.get('unit', '')
                )
                for m in measurements
            ]
            
            if data_points:
                series[sensor['name']] = data_points
        
        return ComparisonResponse(
            title=f"Comparison: {mtype.get('code', 'Unknown')} ({days} days)",
            series=series
        )
    
    @staticmethod
    def get_sensor_statistics(
        sensor_id: int,
        measurement_type_id: Optional[int] = None,
        days: int = 7
    ) -> SensorStatistics:
        """Get detailed statistics for a sensor."""
        repo = get_repository()
        
        sensor = repo.get_sensor_by_id(sensor_id)
        if not sensor:
            raise ValueError(f"Sensor {sensor_id} not found")
        
        stats = repo.get_sensor_statistics(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            days=days
        )
        
        # Enrich with sensor and type info
        types = {t['id']: t for t in repo.get_measurement_types()}
        
        measurements = []
        if 'measurements' in stats:
            for m in stats['measurements']:
                mtype = types.get(m.get('measurement_type_id', 0), {})
                measurements.append(MeasurementResponse(
                    time=datetime.fromisoformat(m['time']),
                    sensor_id=m['sensor_id'],
                    measurement_type_id=m['measurement_type_id'],
                    statistic_id=m.get('statistic_id'),
                    value_num=m['value_num'],
                    internal_count=m['internal_count'],
                    sensor_name=sensor['name'],
                    measurement_type_code=mtype.get('code'),
                    measurement_type_unit=mtype.get('unit')
                ))
        
        return SensorStatistics(
            sensor_id=sensor_id,
            sensor_name=sensor['name'],
            measurement_type_code=types.get(measurement_type_id, {}).get('code') if measurement_type_id else None,
            count=stats.get('count', 0),
            min=stats.get('min'),
            max=stats.get('max'),
            avg=stats.get('avg'),
            latest=stats.get('latest'),
            measurements=measurements
        )
    
    @staticmethod
    def get_latest_readings() -> dict:
        """Get latest reading for each measurement type from active sensors."""
        repo = get_repository()
        
        sensors = repo.get_sensors()
        types = {t['id']: t for t in repo.get_measurement_types()}
        
        latest_by_type = {}
        
        for mtype in types.values():
            latest = None
            for sensor in sensors:
                if not sensor['active']:
                    continue
                
                measurement = repo.get_latest_measurement(
                    sensor_id=sensor['id'],
                    measurement_type_id=mtype['id']
                )
                
                if measurement:
                    if latest is None or datetime.fromisoformat(measurement['time']) > datetime.fromisoformat(latest['time']):
                        latest = measurement
                        latest['sensor_name'] = sensor['name']
            
            if latest:
                latest_by_type[mtype['code']] = {
                    'value': latest['value_num'],
                    'unit': mtype['unit'],
                    'sensor': latest.get('sensor_name'),
                    'time': latest['time']
                }
        
        return latest_by_type
