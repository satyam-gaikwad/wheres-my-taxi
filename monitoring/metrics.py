"""
Metrics collection for the Where's My Taxi ML pipeline.

This module provides metrics collection capabilities for:
- Model performance tracking
- Data quality monitoring  
- Pipeline health monitoring
"""

import time
import psutil
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


@dataclass
class ModelMetrics:
    """Model performance metrics."""
    timestamp: str
    model_type: str
    mse: float
    r2_score: float
    mae: float
    training_samples: int
    training_duration: float
    feature_count: int
    
    @classmethod
    def from_model_training(cls, model, X, y, model_type: str = "SGDRegressor", 
                          training_duration: float = 0.0):
        """Create metrics from trained model and data."""
        y_pred = model.predict(X)
        
        return cls(
            timestamp=datetime.utcnow().isoformat(),
            model_type=model_type,
            mse=mean_squared_error(y, y_pred),
            r2_score=r2_score(y, y_pred),
            mae=mean_absolute_error(y, y_pred),
            training_samples=len(X),
            training_duration=training_duration,
            feature_count=X.shape[1] if hasattr(X, 'shape') else len(X[0])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DataQualityMetrics:
    """Data quality metrics."""
    timestamp: str
    total_records: int
    valid_records: int
    invalid_records: int
    missing_values: int
    duplicate_records: int
    outliers_removed: int
    data_quality_score: float
    
    @classmethod
    def from_data_processing(cls, original_data: pd.DataFrame, 
                           processed_data: pd.DataFrame,
                           outliers_removed: int = 0):
        """Create metrics from data processing."""
        missing_values = original_data.isnull().sum().sum()
        duplicates = original_data.duplicated().sum()
        
        return cls(
            timestamp=datetime.utcnow().isoformat(),
            total_records=len(original_data),
            valid_records=len(processed_data),
            invalid_records=len(original_data) - len(processed_data),
            missing_values=missing_values,
            duplicate_records=duplicates,
            outliers_removed=outliers_removed,
            data_quality_score=len(processed_data) / len(original_data) if len(original_data) > 0 else 0.0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PipelineMetrics:
    """Pipeline execution metrics."""
    timestamp: str
    pipeline_name: str
    status: str  # "success", "failure", "warning"
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    files_processed: int
    errors: List[str]
    warnings: List[str]
    
    @classmethod
    def create_empty(cls, pipeline_name: str = "wheres_my_taxi_pipeline"):
        """Create empty metrics for pipeline start."""
        return cls(
            timestamp=datetime.utcnow().isoformat(),
            pipeline_name=pipeline_name,
            status="running",
            execution_time=0.0,
            memory_usage_mb=0.0,
            cpu_usage_percent=0.0,
            files_processed=0,
            errors=[],
            warnings=[]
        )
    
    def update_system_metrics(self):
        """Update system resource metrics."""
        process = psutil.Process()
        self.memory_usage_mb = process.memory_info().rss / 1024 / 1024
        self.cpu_usage_percent = process.cpu_percent()
    
    def add_error(self, error: str):
        """Add an error to the metrics."""
        self.errors.append(error)
        if self.status != "failure":
            self.status = "failure"
    
    def add_warning(self, warning: str):
        """Add a warning to the metrics."""
        self.warnings.append(warning)
        if self.status == "running":
            self.status = "warning"
    
    def complete_successfully(self, execution_time: float, files_processed: int = 0):
        """Mark pipeline as successfully completed."""
        self.execution_time = execution_time
        self.files_processed = files_processed
        if self.status == "running":
            self.status = "success"
        self.update_system_metrics()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MetricsCollector:
    """Central metrics collector for the pipeline."""
    
    def __init__(self):
        self.model_metrics: Optional[ModelMetrics] = None
        self.data_quality_metrics: Optional[DataQualityMetrics] = None
        self.pipeline_metrics: Optional[PipelineMetrics] = None
        self.start_time: float = time.time()
    
    def start_pipeline(self, pipeline_name: str = "wheres_my_taxi_pipeline"):
        """Start pipeline metrics collection."""
        self.pipeline_metrics = PipelineMetrics.create_empty(pipeline_name)
        self.start_time = time.time()
    
    def collect_model_metrics(self, model, X, y, model_type: str = "SGDRegressor"):
        """Collect model performance metrics."""
        training_duration = time.time() - self.start_time
        self.model_metrics = ModelMetrics.from_model_training(
            model, X, y, model_type, training_duration
        )
    
    def collect_data_quality_metrics(self, original_data: pd.DataFrame, 
                                   processed_data: pd.DataFrame,
                                   outliers_removed: int = 0):
        """Collect data quality metrics."""
        self.data_quality_metrics = DataQualityMetrics.from_data_processing(
            original_data, processed_data, outliers_removed
        )
    
    def complete_pipeline(self, files_processed: int = 0):
        """Complete pipeline metrics collection."""
        if self.pipeline_metrics:
            execution_time = time.time() - self.start_time
            self.pipeline_metrics.complete_successfully(execution_time, files_processed)
    
    def add_pipeline_error(self, error: str):
        """Add error to pipeline metrics."""
        if self.pipeline_metrics:
            self.pipeline_metrics.add_error(error)
    
    def add_pipeline_warning(self, warning: str):
        """Add warning to pipeline metrics."""
        if self.pipeline_metrics:
            self.pipeline_metrics.add_warning(warning)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        metrics = {}
        
        if self.pipeline_metrics:
            metrics['pipeline'] = self.pipeline_metrics.to_dict()
        
        if self.model_metrics:
            metrics['model'] = self.model_metrics.to_dict()
        
        if self.data_quality_metrics:
            metrics['data_quality'] = self.data_quality_metrics.to_dict()
        
        return metrics