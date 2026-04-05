# Architecture - Storage Layer (CSV/PostgreSQL Abstraction)

## Overview

The **Storage Layer** provides a clean abstraction that allows switching between **CSV files (current)** and **PostgreSQL (future)** without changing any business logic.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│          FastAPI Application (main.py)              │
├─────────────────────────────────────────────────────┤
│
│  ┌──────────────────────────────────────────────┐
│  │   Routers & Services                         │
│  │  (sensors, measurements, statistics, etc.)   │
│  └──────────┬───────────────────────────────────┘
│             │ Uses BaseRepository interface
│             │
│  ┌──────────▼───────────────────────────────────┐
│  │   Storage Layer (__init__.py)                │
│  │   - init_repository()                        │
│  │   - get_repository()                         │
│  └──────────┬───────────────────────────────────┘
│             │
│       ┌─────┴──────────────────────┐
│       │                            │
│  ┌────▼─────────────┐    ┌────────▼────────┐
│  │  CSVRepository   │    │ PostgreSQLRepo  │
│  │  (Current)       │    │ (Future)        │
│  │                  │    │                 │
│  │ Reads:           │    │ Connects to:    │
│  │ /backend/data/   │    │ PostgreSQL DB   │
│  └──────────────────┘    └─────────────────┘
│       │                            │
│  ┌────▼──────────────────┐    ┌───▼──────────────┐
│  │  CSV Files            │    │  PostgreSQL      │
│  │  - sensors.csv        │    │  - sensors       │
│  │  - measurements.csv   │    │  - measurements  │
│  │  - measurement_types  │    │  - measurement_  │
│  │  - statistics_dim.csv │    │    types         │
│  └───────────────────────┘    │  - statistics_   │
│                                │    dimension     │
│                                └──────────────────┘
```

## How It Works

### Current State: CSV Mode

1. **CSV Files** in `/backend/data/` contain tables exported from pgAdmin
2. **CSVRepository** reads these files into memory when app starts
3. **Services** query the repository without knowing if it's CSV or DB
4. **FastAPI routes** expose this data via REST API

### Future State: PostgreSQL Mode

Once you have PostgreSQL credentials:

1. Uncomment `repository_pg.py` implementation
2. Call `init_repository(source='postgresql', pg_connection_string='...')`
3. Everything else works **unchanged**

## File Structure

```
backend/
├── storage/                      # Storage abstraction layer
│   ├── __init__.py              # Factory & initialization
│   ├── base_repository.py       # Abstract interface
│   ├── repository_csv.py        # CSV implementation
│   └── repository_pg.py         # PostgreSQL stub (future)
│
├── data/                         # CSV files (current data source)
│   ├── sensors.csv              # Sensor list
│   ├── measurements.csv         # All measurements
│   ├── measurement_types.csv    # Types (TEMP, HUM, LUX, etc.)
│   └── statistics_dimension.csv # Stats types (MIN, MAX, AVG, etc.)
│
├── app/
│   ├── main.py                  # Initializes storage layer
│   ├── services/
│   │   ├── measurements_service.py
│   │   ├── stats_service.py
│   │   └── ...
│   └── routers/
│       ├── measurements_router.py
│       ├── stats_router.py
│       └── ...
```

## CSV Schema

### sensors.csv
```csv
id,EUI64,Nom,Réservoir,activé,Métadonnées,display_order
1,A81758FFFE111111,Sensor_Hall_Temp,Hall A,true,{"location":"entry"},1
```

### measurements.csv
```csv
time,sensor_id,measurement_type_id,statistic_id,value_num,internal_count
2026-04-05T23:00:00,1,1,1,22.5,1
```

### measurement_types.csv
```csv
id,Code,Unité,value_domain,Description
1,TEMP,°C,-50 to 60,Temperature in Celsius
```

### statistics_dimension.csv
```csv
id,Code,Description
1,RAW,Raw instantaneous value
4,AVG,Average value in period
```

## Usage in Code

### Initialize Storage
```python
from backend.storage import init_repository, get_repository

# On app startup (in main.py):
init_repository(source='csv', csv_data_dir='./backend/data')

# Later, when ready to switch to PostgreSQL:
# init_repository(source='postgresql', pg_connection_string='postgresql://user:pass@host/db')
```

### Query Data in Services
```python
from backend.storage import get_repository

def get_measurements():
    repo = get_repository()  # Works whether it's CSV or DB
    
    # Same API regardless of source:
    measurements = repo.get_measurements(
        sensor_id=1,
        measurement_type_id=2,
        days=7
    )
    return measurements
```

## Switching to PostgreSQL

When you have PostgreSQL credentials:

1. **Fill in connection details**:
   ```python
   # In main.py
   pg_connection_string = "postgresql://user:password@host:5432/sensor_db"
   init_repository(source='postgresql', pg_connection_string=pg_connection_string)
   ```

2. **Implement repository_pg.py** (currently stubbed):
   ```python
   def get_measurements(self, ...):
       with self.engine.connect() as conn:
           result = conn.execute(
               text("SELECT * FROM measurements WHERE ...")
           )
           return [dict(row) for row in result]
   ```

3. **Update database.py** for SQLAlchemy models if using ORM

4. **No other code changes needed!** Everything else uses the abstraction.

## Benefits

✅ **Separation of Concerns** - Data source logic isolated  
✅ **Easy Testing** - Mock repository for unit tests  
✅ **Flexibility** - Switch sources without refactoring services  
✅ **Gradual Migration** - CSV → PostgreSQL without app downtime  
✅ **Extensibility** - Add new sources (MongoDB, Elasticsearch, etc.)  

## Tables in PostgreSQL (for reference)

```sql
CREATE TABLE sensors (
    id INT PRIMARY KEY,
    EUI64 VARCHAR,
    Nom VARCHAR,
    Réservoir VARCHAR,
    activé BOOLEAN,
    Métadonnées JSON,
    display_order INT
);

CREATE TABLE measurements (
    time TIMESTAMP,
    sensor_id INT REFERENCES sensors(id),
    measurement_type_id INT REFERENCES measurement_types(id),
    statistic_id INT REFERENCES statistics_dimension(id),
    value_num FLOAT,
    internal_count INT
);

CREATE TABLE measurement_types (
    id INT PRIMARY KEY,
    Code VARCHAR,
    Unité VARCHAR,
    value_domain VARCHAR,
    Description VARCHAR
);

CREATE TABLE statistics_dimension (
    id INT PRIMARY KEY,
    Code VARCHAR,
    Description VARCHAR
);
```

## Next Steps

1. **CSV Mode (NOW)**:
   - Export tables from pgAdmin to CSV
   - Place in `/backend/data/`
   - Run app with CSV repository

2. **PostgreSQL Mode (WHEN READY)**:
   - Get credentials from your DB admin
   - Implement `repository_pg.py`
   - Uncomment PostgreSQL calls in `main.py`
   - Run tests to verify all endpoints work

---

**Status**: ✅ CSV implementation complete | ⏳ PostgreSQL implementation pending credentials
