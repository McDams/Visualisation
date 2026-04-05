"""
Data validation module - validates sensor data quality and consistency.
"""

import os
import csv
from datetime import datetime
from typing import List, Tuple


class DataValidator:
    """Validates sensor data for quality and consistency."""
    
    def __init__(self, sensor_type: str, min_value: float = None, max_value: float = None):
        """
        Initialize validator.
        
        Args:
            sensor_type: Type of sensor (temperature, humidity, light)
            min_value: Minimum acceptable value
            max_value: Maximum acceptable value
        """
        self.sensor_type = sensor_type
        self.min_value = min_value
        self.max_value = max_value
        self.errors = []
        self.warnings = []
    
    def validate_value(self, value: float, row_num: int = None) -> bool:
        """
        Validate a single sensor value.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            val = float(value)
            
            # Check bounds
            if self.min_value is not None and val < self.min_value:
                msg = f"Value {val} below minimum ({self.min_value})"
                if row_num:
                    msg = f"Row {row_num}: {msg}"
                self.warnings.append(msg)
                return False
            
            if self.max_value is not None and val > self.max_value:
                msg = f"Value {val} above maximum ({self.max_value})"
                if row_num:
                    msg = f"Row {row_num}: {msg}"
                self.warnings.append(msg)
                return False
            
            return True
        
        except ValueError:
            self.errors.append(f"Row {row_num}: Invalid numeric value: {value}")
            return False
    
    def validate_timestamp(self, timestamp_str: str, row_num: int = None) -> bool:
        """Validate timestamp format."""
        try:
            datetime.fromisoformat(timestamp_str)
            return True
        except (ValueError, TypeError):
            msg = f"Invalid timestamp format: {timestamp_str} (expected: ISO format)"
            if row_num:
                msg = f"Row {row_num}: {msg}"
            self.errors.append(msg)
            return False
    
    def validate_csv_file(self, csv_file_path: str) -> Tuple[bool, dict]:
        """
        Validate entire CSV file.
        
        Returns:
            Tuple of (is_valid, stats_dict)
        """
        if not os.path.exists(csv_file_path):
            self.errors.append(f"File not found: {csv_file_path}")
            return False, {}
        
        valid_rows = 0
        invalid_rows = 0
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                    timestamp_valid = self.validate_timestamp(row.get('timestamp'), row_num)
                    value_valid = self.validate_value(row.get('value'), row_num)
                    
                    if timestamp_valid and value_valid:
                        valid_rows += 1
                    else:
                        invalid_rows += 1
        
        except Exception as e:
            self.errors.append(f"Error reading CSV file: {e}")
            return False, {}
        
        stats = {
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "total_rows": valid_rows + invalid_rows,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }
        
        is_valid = invalid_rows == 0 and len(self.errors) == 0
        return is_valid, stats


def validate_sensor_readings(
    csv_file_path: str,
    sensor_type: str,
    min_value: float = None,
    max_value: float = None
) -> dict:
    """
    Validate sensor readings from CSV file.
    
    Returns:
        Dictionary with validation results
    """
    validator = DataValidator(sensor_type, min_value, max_value)
    is_valid, stats = validator.validate_csv_file(csv_file_path)
    
    return {
        "is_valid": is_valid,
        "file": csv_file_path,
        "sensor_type": sensor_type,
        "stats": stats,
        "errors": validator.errors,
        "warnings": validator.warnings
    }


def print_validation_report(results: dict):
    """Pretty print validation results."""
    print(f"\n📋 Validation Report for: {results['file']}")
    print(f"📊 Sensor Type: {results['sensor_type']}")
    print(f"✓ Valid: {results['stats']['valid_rows']}")
    print(f"✗ Invalid: {results['stats']['invalid_rows']}")
    print(f"📌 Total: {results['stats']['total_rows']}")
    
    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for error in results['errors'][:10]:  # Show first 10
            print(f"  - {error}")
    
    if results['warnings']:
        print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
        for warning in results['warnings'][:10]:  # Show first 10
            print(f"  - {warning}")
    
    status = "✅ VALID" if results['is_valid'] else "❌ INVALID"
    print(f"\n{status}")


if __name__ == "__main__":
    # Example usage
    print("🚀 Data Validation utility")
    
    # Example: validate temperature data
    # results = validate_sensor_readings("data/temperature.csv", "temperature", min_value=-50, max_value=60)
    # print_validation_report(results)
