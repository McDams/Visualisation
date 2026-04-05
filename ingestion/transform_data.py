"""
Data transformation module - transforms raw data to standardized format.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class DataTransformer:
    """Transforms raw sensor data into standardized format."""
    
    @staticmethod
    def standardize_timestamp(timestamp_str: str) -> datetime:
        """
        Standardize various timestamp formats to ISO format.
        
        Supports:
        - ISO format: 2024-01-01T10:30:00
        - US format: 01/01/2024 10:30:00
        - European format: 01-01-2024 10:30:00
        """
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%m/%d/%Y %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse timestamp: {timestamp_str}")
    
    @staticmethod
    def normalize_value(value: float, sensor_type: str) -> float:
        """
        Normalize sensor values to standard ranges.
        
        Temperature: Celsius (-50 to 60)
        Humidity: Percentage (0-100)
        Light: Lux (0-1000+)
        """
        # Add custom normalization logic as needed
        return float(value)
    
    @staticmethod
    def detect_outliers(values: List[float], threshold: float = 2.0) -> List[int]:
        """
        Detect outliers using z-score method.
        
        Returns:
            List of indices of detected outliers
        """
        import statistics
        
        if len(values) < 2:
            return []
        
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        
        outliers = []
        for i, value in enumerate(values):
            if stdev > 0:
                z_score = abs((value - mean) / stdev)
                if z_score > threshold:
                    outliers.append(i)
        
        return outliers
    
    @staticmethod
    def resample_data(
        df: pd.DataFrame,
        frequency: str = 'H',
        aggregation: str = 'mean'
    ) -> pd.DataFrame:
        """
        Resample timeseries data to different frequency.
        
        Frequencies:
        - 'D': Daily
        - 'H': Hourly
        - '15T': 15-minute
        - 'min': Minute
        
        Aggregations:
        - 'mean': Average
        - 'sum': Sum
        - 'min': Minimum
        - 'max': Maximum
        """
        if not isinstance(df, pd.DataFrame):
            return df
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        if aggregation == 'mean':
            return df.resample(frequency).mean()
        elif aggregation == 'sum':
            return df.resample(frequency).sum()
        elif aggregation == 'min':
            return df.resample(frequency).min()
        elif aggregation == 'max':
            return df.resample(frequency).max()
        else:
            return df.resample(frequency).mean()
    
    @staticmethod
    def merge_multiple_sensors(
        data_list: List[Dict],
        join_type: str = 'inner'
    ) -> pd.DataFrame:
        """
        Merge data from multiple sensors.
        
        Args:
            data_list: List of dictionaries with sensor data
            join_type: 'inner', 'outer', 'left', 'right'
        """
        dfs = []
        
        for sensor_data in data_list:
            df = pd.DataFrame(sensor_data['readings'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            df = df.rename(columns={'value': f"{sensor_data['name']}"})
            dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        result = dfs[0]
        for df in dfs[1:]:
            result = result.join(df, how=join_type)
        
        return result.reset_index()


def transform_csv_to_dataframe(csv_path: str) -> pd.DataFrame:
    """Convert CSV file to pandas DataFrame with transformations."""
    df = pd.read_csv(csv_path)
    
    # Standardize timestamp
    df['timestamp'] = df['timestamp'].apply(DataTransformer.standardize_timestamp)
    
    # Ensure value is numeric
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    
    # Remove any NaN values introduced by conversion errors
    df = df.dropna()
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    return df


def apply_moving_average(
    values: List[float],
    window: int = 3
) -> List[float]:
    """Apply moving average smoothing to data."""
    if len(values) < window:
        return values
    
    smoothed = []
    for i in range(len(values)):
        start = max(0, i - window // 2)
        end = min(len(values), i + window // 2 + 1)
        smoothed.append(sum(values[start:end]) / (end - start))
    
    return smoothed


def interpolate_missing_values(
    df: pd.DataFrame,
    method: str = 'linear'
) -> pd.DataFrame:
    """
    Interpolate missing values in dataframe.
    
    Methods:
    - 'linear': Linear interpolation
    - 'forward_fill': Forward fill
    - 'backward_fill': Backward fill
    """
    if method == 'linear':
        return df.interpolate(method='linear')
    elif method == 'forward_fill':
        return df.fillna(method='ffill')
    elif method == 'backward_fill':
        return df.fillna(method='bfill')
    else:
        return df


if __name__ == "__main__":
    print("🚀 Data Transformation utility")
    print("Available transformations:")
    print("  - Timestamp standardization")
    print("  - Value normalization")
    print("  - Outlier detection")
    print("  - Data resampling")
    print("  - Multi-sensor merging")
