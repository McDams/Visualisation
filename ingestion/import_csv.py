"""
CSV Import module - loads sensor data from CSV files into the database.
"""

import csv
import os
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.database import SessionLocal, engine, Base
from backend.app.models.db_models import Sensor, SensorReading, SensorType


def import_csv_file(
    csv_file_path: str,
    sensor_id: int,
    db: Session,
    skip_header: bool = True
) -> tuple[int, int]:
    """
    Import sensor readings from a CSV file.
    
    Expected CSV format:
    timestamp,value
    2024-01-01T10:00:00,25.5
    2024-01-01T11:00:00,26.1
    
    Args:
        csv_file_path: Path to CSV file
        sensor_id: ID of existing sensor
        db: Database session
        skip_header: Whether to skip first row
    
    Returns:
        Tuple of (success_count, error_count)
    """
    success_count = 0
    error_count = 0
    
    if not os.path.exists(csv_file_path):
        print(f"❌ File not found: {csv_file_path}")
        return success_count, error_count
    
    # Verify sensor exists
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        print(f"❌ Sensor with ID {sensor_id} not found")
        return success_count, error_count
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        if skip_header:
            next(reader, None)
        
        for row_num, row in enumerate(reader, 1):
            try:
                timestamp_str = row.get('timestamp')
                value_str = row.get('value')
                
                if not timestamp_str or not value_str:
                    print(f"⚠️  Row {row_num}: Missing timestamp or value")
                    error_count += 1
                    continue
                
                # Parse timestamp
                timestamp = datetime.fromisoformat(timestamp_str)
                value = float(value_str)
                
                # Add reading
                reading = SensorReading(
                    sensor_id=sensor_id,
                    value=value,
                    timestamp=timestamp
                )
                db.add(reading)
                success_count += 1
                
                # Commit every 100 rows for performance
                if success_count % 100 == 0:
                    db.commit()
                    print(f"✓ Imported {success_count} readings...")
                
            except ValueError as e:
                print(f"⚠️  Row {row_num}: Invalid data - {e}")
                error_count += 1
            except Exception as e:
                print(f"⚠️  Row {row_num}: Error - {e}")
                error_count += 1
        
        # Final commit
        db.commit()
    
    print(f"✅ Import complete: {success_count} successful, {error_count} errors")
    return success_count, error_count


def bulk_import_directory(
    directory: str,
    db: Session
) -> dict:
    """
    Import all CSV files from a directory.
    Expects structure: sensor_<sensor_id>.csv
    
    Example:
        sensor_1.csv - readings for sensor 1
        sensor_2.csv - readings for sensor 2
    """
    results = {}
    
    if not os.path.isdir(directory):
        print(f"❌ Directory not found: {directory}")
        return results
    
    csv_files = Path(directory).glob("sensor_*.csv")
    
    for csv_file in csv_files:
        # Extract sensor ID from filename
        try:
            sensor_id = int(csv_file.stem.split('_')[1])
        except (IndexError, ValueError):
            print(f"⚠️  Invalid filename format: {csv_file.name} (expected: sensor_<id>.csv)")
            continue
        
        print(f"\n📂 Processing {csv_file.name}...")
        success, errors = import_csv_file(str(csv_file), sensor_id, db)
        results[csv_file.name] = {"success": success, "errors": errors}
    
    return results


if __name__ == "__main__":
    # Example usage
    print("🚀 CSV Import utility")
    print("Usage: python import_csv.py <csv_file> <sensor_id>")
    print("Or: python import_csv.py --directory <data_directory>")
    
    db = SessionLocal()
    try:
        # Example: import single file
        # success, errors = import_csv_file("data/sensor_1.csv", sensor_id=1, db=db)
        
        # Example: import directory
        # results = bulk_import_directory("data", db)
        
        print("\n✅ Ready for CSV import")
    finally:
        db.close()
