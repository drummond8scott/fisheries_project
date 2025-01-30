# src/config/pipeline_config.py

from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import os

class StorageType(Enum):
    """Defines supported storage backends for the pipeline."""
    PARQUET = "parquet"
    ICEBERG = "iceberg"  # Future support

class ExecutionMode(Enum):
    """Defines how Spark jobs will be executed."""
    LOCAL = "local"
    LIVY = "livy"

@dataclass
class ResourceConfig:
    """
    Controls resource allocation and performance tuning.
    These settings affect how Spark processes data, regardless of execution mode.
    """
    driver_memory: str = os.getenv('DRIVER_MEMORY', '2g')
    executor_memory: str = os.getenv('EXECUTOR_MEMORY', '2g')
    executor_cores: int = int(os.getenv('EXECUTOR_CORES', '2'))
    shuffle_partitions: int = int(os.getenv('SHUFFLE_PARTITIONS', '200'))

    def to_spark_conf(self) -> Dict[str, str]:
        """Converts resource settings to Spark configuration."""
        return {
            'spark.driver.memory': self.driver_memory,
            'spark.executor.memory': self.executor_memory,
            'spark.executor.cores': str(self.executor_cores),
            'spark.sql.shuffle.partitions': str(self.shuffle_partitions)
        }

class StorageManager:
    """
    Manages data storage configuration and paths.
    Handles both current Parquet storage and future Iceberg integration.
    """

    def __init__(self):
        self.storage_type = StorageType(os.getenv('STORAGE_TYPE', 'parquet'))
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / 'data'

        # Ensure critical directories exist
        self._initialize_directories()

    def _initialize_directories(self):
        """Creates necessary data directories if they don't exist."""
        (self.data_dir / 'raw').mkdir(parents=True, exist_ok=True)
        (self.data_dir / 'processed').mkdir(parents=True, exist_ok=True)

    def get_storage_config(self) -> Dict[str, Any]:
        """Returns storage-specific configuration."""
        base_config = {
            'type': self.storage_type.value,
            'warehouse_path': str(self.data_dir),
            'raw_path': str(self.data_dir / 'raw'),
            'processed_path': str(self.data_dir / 'processed')
        }

        if self.storage_type == StorageType.PARQUET:
            base_config.update({
                'format': 'parquet',
                'compression': 'snappy',
                'partition_by': ['year', 'month', 'day']
            })
        elif self.storage_type == StorageType.ICEBERG:
            base_config.update({
                'format': 'iceberg',
                'catalog_name': 'fisheries_catalog',
                'warehouse_path': str(self.data_dir / 'warehouse')
            })

        return base_config

class ExecutionManager:
    """
    Manages execution environment configuration.
    Supports both local development and production Livy execution.
    """

    def __init__(self):
        self.mode = ExecutionMode(os.getenv('EXECUTION_MODE', 'local'))
        self.resources = ResourceConfig()

        if self.mode == ExecutionMode.LIVY:
            self.livy_config = {
                'host': os.getenv('LIVY_HOST', 'localhost'),
                'port': int(os.getenv('LIVY_PORT', '8998')),
                'protocol': os.getenv('LIVY_PROTOCOL', 'http'),
                'auth_enabled': os.getenv('LIVY_AUTH_ENABLED', 'false').lower() == 'true'
            }

    def get_spark_conf(self) -> Dict[str, str]:
        """
        Creates complete Spark configuration based on execution mode.
        Combines resource settings with mode-specific configurations.
        """
        conf = {
            **self.resources.to_spark_conf(),
            'spark.sql.adaptive.enabled': 'true',
            'spark.sql.adaptive.coalescePartitions.enabled': 'true'
        }

        if self.mode == ExecutionMode.LIVY:
            conf.update({
                'spark.master': 'yarn',
                'spark.submit.deployMode': 'cluster'
            })

        return conf

class PipelineConfig:
    """
    Central pipeline configuration that integrates all components.
    This is the main entry point for pipeline configuration.
    """

    def __init__(self):
        # Initialize core components
        self.storage = StorageManager()
        self.execution = ExecutionManager()

        # Processing configuration
        self.processing = {
            'batch_size': int(os.getenv('BATCH_SIZE', '10000')),
            'incremental': {
                'enabled': True,
                'tracking_column': 'ingestion_timestamp',
                'watermark_delay': '1 hour'
            }
        }

        # Monitoring configuration
        self.monitoring = {
            'metrics_enabled': True,
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'alert_thresholds': {
                'job_duration_seconds': 3600,
                'error_rate_percent': 5
            }
        }

    def get_dataset_path(self, dataset_name: str, layer: str = 'raw') -> Path:
        """Gets the appropriate path for a dataset in a specific layer."""
        base_path = self.storage.data_dir / layer / dataset_name
        base_path.mkdir(parents=True, exist_ok=True)
        return base_path

    def create_spark_session_config(self, app_name: str) -> Dict[str, str]:
        """
        Creates a complete Spark session configuration.

        Args:
            app_name: Name of the Spark application

        Returns:
            Dictionary of Spark configuration settings
        """
        return {
            **self.execution.get_spark_conf(),
            'spark.app.name': app_name,
            'spark.sql.warehouse.dir': str(self.storage.data_dir)
        }

# Create global configuration instance
config = PipelineConfig()
