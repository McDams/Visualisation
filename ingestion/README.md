# Data Ingestion Pipeline

Processing and importing sensor data from various sources.

## Modules

### `import_csv.py`
Loads sensor readings from CSV files into the database.

**Usage:**
```python
from import_csv import import_csv_file, bulk_import_directory
from app.database import SessionLocal

db = SessionLocal()

# Import single file
success, errors = import_csv_file("data/sensor_1.csv", sensor_id=1, db=db)

# Import entire directory
results = bulk_import_directory("data", db)
```

**CSV Format:**
```csv
timestamp,value
2024-01-01T10:00:00,25.5
2024-01-01T11:00:00,26.1
```

### `validate_data.py`
Validates sensor data for quality and consistency.

**Usage:**
```python
from validate_data import validate_sensor_readings, print_validation_report

results = validate_sensor_readings(
    "data/sensor.csv",
    sensor_type="temperature",
    min_value=-50,
    max_value=60
)
print_validation_report(results)
```

### `transform_data.py`
Transforms raw data into standardized format.

**Features:**
- Timestamp standardization
- Value normalization
- Outlier detection
- Data resampling
- Multi-sensor merging

**Usage:**
```python
from transform_data import transform_csv_to_dataframe, resample_data

df = transform_csv_to_dataframe("data/sensor.csv")
df_resampled = resample_data(df, frequency='H', aggregation='mean')
```

### `scheduler.py`
Schedules periodic data ingestion and processing tasks.

**Usage:**
```python
from scheduler import create_and_start_scheduler

scheduler = create_and_start_scheduler()
# Scheduler runs automatically

# Or manual control:
from scheduler import SensorDataScheduler

scheduler = SensorDataScheduler()
scheduler.schedule_threshold_check(interval_minutes=5)
scheduler.schedule_data_import("data", interval_minutes=30)
scheduler.start()
```

## Typical Workflow

1. **Validate** - Check data quality
2. **Transform** - Standardize format
3. **Import** - Load into database
4. **Monitor** - Check thresholds and create alerts

Example:
```python
from validate_data import validate_sensor_readings
from transform_data import transform_csv_to_dataframe
from import_csv import import_csv_file

# Validate
results = validate_sensor_readings("data/sensor.csv", "temperature")
if results['is_valid']:
    # Transform
    df = transform_csv_to_dataframe("data/sensor.csv")
    
    # Import
    db = SessionLocal()
    success, errors = import_csv_file("data/sensor.csv", sensor_id=1, db=db)
```
