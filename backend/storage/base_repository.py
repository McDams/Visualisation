"""
Abstract base repository for data storage abstraction.
Allows switching between CSV and PostgreSQL without changing business logic.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime


class BaseRepository(ABC):
    """Abstract repository interface."""
    
    @abstractmethod
    def get_sensors(self) -> List[Dict[str, Any]]:
        """Get all sensors."""
        pass
    
    @abstractmethod
    def get_sensor_by_id(self, sensor_id: int) -> Optional[Dict[str, Any]]:
        """Get sensor by ID."""
        pass
    
    @abstractmethod
    def get_measurements(
        self,
        sensor_id: Optional[int] = None,
        measurement_type_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get measurements with optional filters."""
        pass
    
    @abstractmethod
    def get_measurement_types(self) -> List[Dict[str, Any]]:
        """Get all measurement types."""
        pass
    
    @abstractmethod
    def get_statistics_dimension(self) -> List[Dict[str, Any]]:
        """Get all statistics dimensions (MIN, MAX, AVG, etc)."""
        pass
    
    @abstractmethod
    def get_sensor_statistics(
        self,
        sensor_id: int,
        measurement_type_id: Optional[int] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get statistics for a sensor."""
        pass
    
    @abstractmethod
    def get_latest_measurement(
        self,
        sensor_id: Optional[int] = None,
        measurement_type_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get latest measurement."""
        pass
