"""
Storage layer - Abstracts data source (CSV or PostgreSQL).
Allows switching between data sources without changing business logic.
"""

from typing import Literal
from .base_repository import BaseRepository
from .repository_csv import CSVRepository
from .repository_pg import PostgreSQLRepository

# Global repository instance
_repository: BaseRepository = None


def init_repository(
    source: Literal['csv', 'postgresql'] = 'csv',
    pg_connection_string: str = None,
    csv_data_dir: str = "./backend/data"
) -> BaseRepository:
    """
    Initialize repository with specified source.
    
    Args:
        source: Data source type ('csv' or 'postgresql')
        pg_connection_string: PostgreSQL connection string (if source='postgresql')
        csv_data_dir: CSV data directory (if source='csv')
    
    Returns:
        Initialized repository instance
    """
    global _repository
    
    if source == 'csv':
        print("📂 Using CSV repository")
        _repository = CSVRepository(data_dir=csv_data_dir)
    elif source == 'postgresql':
        print("🗄️  Using PostgreSQL repository")
        _repository = PostgreSQLRepository(pg_connection_string)
    else:
        raise ValueError(f"Unknown source: {source}")
    
    return _repository


def get_repository() -> BaseRepository:
    """
    Get current repository instance.
    
    Raises:
        RuntimeError: If repository not initialized
    """
    if _repository is None:
        raise RuntimeError("Repository not initialized. Call init_repository() first.")
    return _repository


# Initialize default repository (CSV)
try:
    init_repository(source='csv')
except Exception as e:
    print(f"❌ Failed to initialize repository: {e}")
