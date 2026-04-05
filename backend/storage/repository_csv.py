"""
CSV-based repository implementation.
Reads data from CSV files in /backend/data/ directory.
"""

import csv
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
from .base_repository import BaseRepository


class CSVRepository(BaseRepository):
    """CSV-based data repository."""
    
    def __init__(self, data_dir: str = "./backend/data"):
        """
        Initialize CSV repository.
        
        Args:
            data_dir: Directory containing CSV files
        """
        self.data_dir = data_dir
        self._ensure_directory()
        self._cache = {}
        self._load_all_data()
    
    def _ensure_directory(self):
        """Ensure data directory exists."""
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_all_data(self):
        """Load all CSV files into cache."""
        self._load_sensors()
        self._load_measurement_types()
        self._load_statistics_dimension()
        self._load_measurements()
    
    def _load_csv(self, filename: str) -> List[Dict]:
        """Load CSV file."""
        filepath = os.path.join(self.data_dir, filename)
        data = []
        
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}")
            return data
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            print(f"✅ Loaded {len(data)} rows from {filename}")
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
        
        return data
    
    def _load_sensors(self):
        """Load sensors.csv"""
        self._cache['sensors'] = self._load_csv('sensors.csv')
    
    def _load_measurement_types(self):
        """Load measurement_types.csv"""
        self._cache['measurement_types'] = self._load_csv('measurement_types.csv')
    
    def _load_statistics_dimension(self):
        """Load statistics_dimension.csv"""
        self._cache['statistics_dimension'] = self._load_csv('statistics_dimension.csv')
    
    def _load_measurements(self):
        """Load measurements.csv"""
        self._cache['measurements'] = self._load_csv('measurements.csv')
    
    # ============= SENSORS =============
    
    def get_sensors(self) -> List[Dict[str, Any]]:
        """Get all sensors."""
        sensors = self._cache.get('sensors', [])
        return [
            {
                'id': int(s.get('id', 0)),
                'eui64': s.get('EUI64', ''),
                'name': s.get('Nom', ''),
                'reservoir': s.get('Réservoir', ''),
                'active': s.get('activé', 'true').lower() == 'true',
                'metadata': s.get('Métadonnées', ''),
                'display_order': int(s.get('display_order', 0))
            }
            for s in sensors
        ]
    
    def get_sensor_by_id(self, sensor_id: int) -> Optional[Dict[str, Any]]:
        """Get sensor by ID."""
        for sensor in self.get_sensors():
            if sensor['id'] == sensor_id:
                return sensor
        return None
    
    # ============= MEASUREMENT TYPES =============
    
    def get_measurement_types(self) -> List[Dict[str, Any]]:
        """Get all measurement types."""
        types = self._cache.get('measurement_types', [])
        return [
            {
                'id': int(t.get('id', 0)),
                'code': t.get('Code', ''),
                'unit': t.get('Unité', ''),
                'value_domain': t.get('value_domain', ''),
                'description': t.get('Description', '')
            }
            for t in types
        ]
    
    # ============= STATISTICS DIMENSION =============
    
    def get_statistics_dimension(self) -> List[Dict[str, Any]]:
        """Get all statistics dimensions."""
        stats = self._cache.get('statistics_dimension', [])
        return [
            {
                'id': int(s.get('id', 0)),
                'code': s.get('Code', ''),
                'description': s.get('Description', '')
            }
            for s in stats
        ]
    
    # ============= MEASUREMENTS =============
    
    def get_measurements(
        self,
        sensor_id: Optional[int] = None,
        measurement_type_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get measurements with optional filters."""
        measurements = self._cache.get('measurements', [])
        
        # Filter
        result = []
        for m in measurements:
            if sensor_id and int(m.get('sensor_id', 0)) != sensor_id:
                continue
            if measurement_type_id and int(m.get('measurement_type_id', 0)) != measurement_type_id:
                continue
            
            # Parse time and filter by range
            try:
                mtime = datetime.fromisoformat(m.get('time', ''))
                if start_time and mtime < start_time:
                    continue
                if end_time and mtime > end_time:
                    continue
            except:
                pass
            
            result.append({
                'time': m.get('time', ''),
                'sensor_id': int(m.get('sensor_id', 0)),
                'measurement_type_id': int(m.get('measurement_type_id', 0)),
                'statistic_id': int(m.get('statistic_id', 0)) if m.get('statistic_id') else None,
                'value_num': float(m.get('value_num', 0)),
                'internal_count': int(m.get('internal_count', 1))
            })
        
        # Sort by time (newest first)
        result.sort(key=lambda x: x['time'], reverse=True)
        
        return result[:limit]
    
    def get_latest_measurement(
        self,
        sensor_id: Optional[int] = None,
        measurement_type_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get latest measurement."""
        measurements = self.get_measurements(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            limit=1
        )
        return measurements[0] if measurements else None
    
    def get_sensor_statistics(
        self,
        sensor_id: int,
        measurement_type_id: Optional[int] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get statistics for a sensor."""
        from datetime import timedelta
        
        start_time = datetime.utcnow() - timedelta(days=days)
        measurements = self.get_measurements(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            start_time=start_time
        )
        
        if not measurements:
            return {
                'sensor_id': sensor_id,
                'count': 0,
                'min': None,
                'max': None,
                'avg': None,
                'latest': None
            }
        
        values = [m['value_num'] for m in measurements]
        
        return {
            'sensor_id': sensor_id,
            'count': len(values),
            'min': round(min(values), 2),
            'max': round(max(values), 2),
            'avg': round(sum(values) / len(values), 2),
            'latest': round(values[0], 2) if values else None,
            'measurements': measurements
        }
    
    def reload(self):
        """Reload all data from CSV files."""
        self._load_all_data()
