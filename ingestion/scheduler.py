"""
Scheduler module - schedules periodic data ingestion and processing tasks.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.database import SessionLocal
from backend.app.services.sensors_service import SensorService
from backend.app.services.alerts_service import AlertService
from validate_data import validate_sensor_readings
from transform_data import transform_csv_to_dataframe
from import_csv import import_csv_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SensorDataScheduler:
    """Manages scheduled tasks for sensor data processing."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(timezone='UTC')
    
    def schedule_threshold_check(self, interval_minutes: int = 5):
        """
        Schedule periodic threshold checks for alerts.
        
        Args:
            interval_minutes: How often to check (in minutes)
        """
        self.scheduler.add_job(
            self._check_thresholds,
            IntervalTrigger(minutes=interval_minutes),
            id='check_thresholds',
            name='Check sensor thresholds',
            replace_existing=True
        )
        logger.info(f"Scheduled threshold checks every {interval_minutes} minutes")
    
    def schedule_data_import(self, directory: str, interval_minutes: int = 30):
        """
        Schedule periodic CSV data import from directory.
        
        Args:
            directory: Directory containing CSV files
            interval_minutes: How often to import (in minutes)
        """
        self.scheduler.add_job(
            self._import_data,
            IntervalTrigger(minutes=interval_minutes),
            args=[directory],
            id='import_data',
            name='Import CSV data',
            replace_existing=True
        )
        logger.info(f"Scheduled data import every {interval_minutes} minutes from {directory}")
    
    def schedule_daily_cleanup(self, hour: int = 2, minute: int = 0):
        """
        Schedule daily data cleanup/aggregation.
        
        Args:
            hour: Hour of day to run (0-23)
            minute: Minute of hour (0-59)
        """
        self.scheduler.add_job(
            self._daily_cleanup,
            CronTrigger(hour=hour, minute=minute),
            id='daily_cleanup',
            name='Daily cleanup',
            replace_existing=True
        )
        logger.info(f"Scheduled daily cleanup at {hour:02d}:{minute:02d} UTC")
    
    @staticmethod
    def _check_thresholds():
        """Check sensor thresholds and create alerts if needed."""
        try:
            db = SessionLocal()
            logger.info("🔍 Checking sensor thresholds...")
            new_alerts = AlertService.check_thresholds(db)
            logger.info(f"✅ Created {len(new_alerts)} new alerts")
            db.close()
        except Exception as e:
            logger.error(f"❌ Error checking thresholds: {e}")
    
    @staticmethod
    def _import_data(directory: str):
        """Import CSV data from directory."""
        try:
            db = SessionLocal()
            logger.info(f"📥 Importing data from {directory}...")
            
            from import_csv import bulk_import_directory
            results = bulk_import_directory(directory, db)
            
            success_total = sum(r['success'] for r in results.values())
            error_total = sum(r['errors'] for r in results.values())
            
            logger.info(f"✅ Import complete: {success_total} successful, {error_total} errors")
            db.close()
        except Exception as e:
            logger.error(f"❌ Error importing data: {e}")
    
    @staticmethod
    def _daily_cleanup():
        """Perform daily maintenance tasks."""
        try:
            db = SessionLocal()
            logger.info("🧹 Running daily cleanup...")
            
            # Example: Archive old data (older than 1 year)
            # Implement as needed
            
            logger.info("✅ Cleanup complete")
            db.close()
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Scheduler stopped")
    
    def get_jobs(self):
        """Get list of scheduled jobs."""
        return self.scheduler.get_jobs()


def create_and_start_scheduler() -> SensorDataScheduler:
    """
    Factory function to create and start the scheduler with default jobs.
    """
    scheduler = SensorDataScheduler()
    
    # Schedule default jobs
    scheduler.schedule_threshold_check(interval_minutes=5)
    scheduler.schedule_daily_cleanup(hour=2, minute=0)
    
    # Uncomment to enable data import scheduling
    # scheduler.schedule_data_import(directory="./data", interval_minutes=30)
    
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    print("🚀 Starting sensor data scheduler...")
    
    scheduler = create_and_start_scheduler()
    
    print("✅ Scheduler running. Press Ctrl+C to stop.")
    
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping scheduler...")
        scheduler.stop()
        print("✅ Scheduler stopped")
