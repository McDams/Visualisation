"""
Statistics service - handles advanced statistical analysis.
Includes distributions, correlations, anomalies, etc.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from backend.storage import get_repository
from app.models.measurement_models import (
    DistributionResponse,
    CorrelationResponse,
    DashboardOverview
)


class StatsService:
    """Service for statistical operations."""
    
    @staticmethod
    def get_distribution(
        measurement_type_id: int,
        sensor_id: Optional[int] = None,
        days: int = 7,
        bins: int = 10
    ) -> DistributionResponse:
        """Generate histogram/distribution data."""
        repo = get_repository()
        
        start_time = datetime.utcnow() - timedelta(days=days)
        measurements = repo.get_measurements(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            start_time=start_time
        )
        
        if not measurements:
            return DistributionResponse(
                title="No data",
                unit="",
                bins=[],
                labels=[],
                count=0
            )
        
        values = [m['value_num'] for m in measurements]
        
        # Calculate histogram
        min_val = min(values)
        max_val = max(values)
        bin_width = (max_val - min_val) / bins if max_val > min_val else 1
        
        bin_counts = [0] * bins
        bin_labels = []
        
        for i in range(bins):
            bin_start = min_val + (i * bin_width)
            bin_end = bin_start + bin_width
            bin_labels.append(f"{bin_start:.1f}-{bin_end:.1f}")
            
            for val in values:
                if bin_start <= val <= bin_end or (i == bins - 1 and val == max_val):
                    bin_counts[i] += 1
        
        types = {t['id']: t for t in repo.get_measurement_types()}
        mtype = types.get(measurement_type_id, {})
        
        title = f"Distribution: {mtype.get('code', 'Unknown')} ({days} days)"
        
        return DistributionResponse(
            title=title,
            unit=mtype.get('unit', ''),
            bins=bin_counts,
            labels=bin_labels,
            count=len(values)
        )
    
    @staticmethod
    def get_correlation(
        measurement_type_id: int,
        sensor1_id: int,
        sensor2_id: int,
        days: int = 7
    ) -> CorrelationResponse:
        """Calculate correlation between two sensors."""
        repo = get_repository()
        
        sensors = {s['id']: s for s in repo.get_sensors()}
        types = {t['id']: t for t in repo.get_measurement_types()}
        
        sensor1 = sensors.get(sensor1_id)
        sensor2 = sensors.get(sensor2_id)
        
        if not sensor1 or not sensor2:
            raise ValueError("One or both sensors not found")
        
        start_time = datetime.utcnow() - timedelta(days=days)
        
        # Align measurements by time
        measurements1 = repo.get_measurements(
            sensor_id=sensor1_id,
            measurement_type_id=measurement_type_id,
            start_time=start_time
        )
        
        measurements2 = repo.get_measurements(
            sensor_id=sensor2_id,
            measurement_type_id=measurement_type_id,
            start_time=start_time
        )
        
        # Create time-indexed dictionaries
        time_dict1 = {m['time']: m['value_num'] for m in measurements1}
        time_dict2 = {m['time']: m['value_num'] for m in measurements2}
        
        # Find common times
        common_times = set(time_dict1.keys()) & set(time_dict2.keys())
        
        if len(common_times) < 2:
            correlation = 0.0
        else:
            values1 = [time_dict1[t] for t in common_times]
            values2 = [time_dict2[t] for t in common_times]
            
            # Calculate Pearson correlation coefficient
            correlation = StatsService._pearson_correlation(values1, values2)
        
        mtype = types.get(measurement_type_id, {})
        
        return CorrelationResponse(
            title=f"Correlation: {sensor1['name']} vs {sensor2['name']}",
            sensor1=sensor1['name'],
            sensor2=sensor2['name'],
            correlation=round(correlation, 3),
            data_points_count=len(common_times)
        )
    
    @staticmethod
    def get_dashboard_overview() -> DashboardOverview:
        """Get dashboard overview with key metrics."""
        repo = get_repository()
        
        sensors = repo.get_sensors()
        active_sensors = [s for s in sensors if s['active']]
        
        # Count measurements
        all_measurements = repo.get_measurements(limit=1000000)
        
        # Get latest readings
        latest_readings = {}
        types = {t['id']: t for t in repo.get_measurement_types()}
        
        for mtype in types.values():
            latest = repo.get_latest_measurement(measurement_type_id=mtype['id'])
            if latest:
                latest_readings[mtype['code']] = latest['value_num']
        
        return DashboardOverview(
            timestamp=datetime.utcnow(),
            sensors_count=len(sensors),
            active_sensors=len(active_sensors),
            measurements_count=len(all_measurements),
            latest_readings=latest_readings
        )
    
    @staticmethod
    def detect_anomalies(
        sensor_id: int,
        measurement_type_id: int,
        days: int = 7,
        threshold: float = 2.0
    ) -> dict:
        """
        Detect anomalies using z-score method.
        threshold: z-score threshold (default 2.0 = 95% confidence)
        """
        repo = get_repository()
        
        start_time = datetime.utcnow() - timedelta(days=days)
        measurements = repo.get_measurements(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            start_time=start_time
        )
        
        if len(measurements) < 3:
            return {"anomalies": [], "count": 0}
        
        values = [m['value_num'] for m in measurements]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        anomalies = []
        for i, m in enumerate(measurements):
            if stdev > 0:
                z_score = abs((m['value_num'] - mean) / stdev)
                if z_score > threshold:
                    anomalies.append({
                        'time': m['time'],
                        'value': m['value_num'],
                        'z_score': round(z_score, 2),
                        'expected_range': f"{mean - 2*stdev:.2f} to {mean + 2*stdev:.2f}"
                    })
        
        return {
            "anomalies": anomalies,
            "count": len(anomalies),
            "mean": round(mean, 2),
            "stdev": round(stdev, 2)
        }
    
    @staticmethod
    def get_trend_analysis(
        sensor_id: int,
        measurement_type_id: int,
        days: int = 7
    ) -> dict:
        """Analyze trend (increasing/decreasing/stable)."""
        repo = get_repository()
        
        start_time = datetime.utcnow() - timedelta(days=days)
        measurements = repo.get_measurements(
            sensor_id=sensor_id,
            measurement_type_id=measurement_type_id,
            start_time=start_time,
            limit=10000
        )
        
        if len(measurements) < 2:
            return {"trend": "insufficient_data"}
        
        # Split into first and second half
        mid = len(measurements) // 2
        first_half = [m['value_num'] for m in measurements[mid:]]
        second_half = [m['value_num'] for m in measurements[:mid]]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        change_percent = ((avg_second - avg_first) / avg_first * 100) if avg_first != 0 else 0
        
        if change_percent > 5:
            trend = "increasing"
        elif change_percent < -5:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_percent": round(change_percent, 2),
            "earlier_avg": round(avg_first, 2),
            "recent_avg": round(avg_second, 2)
        }
    
    @staticmethod
    def _pearson_correlation(x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
        
        sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
        sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)
        
        denominator = (sum_sq_x * sum_sq_y) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
