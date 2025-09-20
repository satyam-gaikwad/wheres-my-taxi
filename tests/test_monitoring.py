import unittest
import tempfile
import json
import numpy as np
import pandas as pd
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from monitoring.metrics import (
    ModelMetrics, DataQualityMetrics, PipelineMetrics, MetricsCollector
)
from monitoring.alerts import AlertManager, Alert
from monitoring.reports import ReportGenerator, MonitoringReport


class TestModelMetrics(unittest.TestCase):
    def test_model_metrics_creation(self):
        # Create mock model and data
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([1.0, 2.0, 3.0])
        
        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([1.1, 2.1, 2.9])
        
        metrics = ModelMetrics.from_model_training(mock_model, X, y)
        
        self.assertEqual(metrics.model_type, "SGDRegressor")
        self.assertEqual(metrics.training_samples, 3)
        self.assertEqual(metrics.feature_count, 2)
        self.assertIsInstance(metrics.mse, float)
        self.assertIsInstance(metrics.r2_score, float)
        self.assertIsInstance(metrics.mae, float)
    
    def test_model_metrics_to_dict(self):
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([1.0, 2.0, 3.0])
        
        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([1.1, 2.1, 2.9])
        
        metrics = ModelMetrics.from_model_training(mock_model, X, y)
        metrics_dict = metrics.to_dict()
        
        self.assertIn('timestamp', metrics_dict)
        self.assertIn('model_type', metrics_dict)
        self.assertIn('mse', metrics_dict)
        self.assertIn('r2_score', metrics_dict)


class TestDataQualityMetrics(unittest.TestCase):
    def test_data_quality_metrics(self):
        # Create sample data
        original_data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [1, 2, None, 4, 5],
            'C': [1, 1, 3, 4, 5]  # Has duplicate
        })
        
        processed_data = pd.DataFrame({
            'A': [1, 2, 4, 5],
            'B': [1, 2, 4, 5],
            'C': [1, 1, 4, 5]
        })
        
        metrics = DataQualityMetrics.from_data_processing(
            original_data, processed_data, outliers_removed=1
        )
        
        self.assertEqual(metrics.total_records, 5)
        self.assertEqual(metrics.valid_records, 4)
        self.assertEqual(metrics.invalid_records, 1)
        self.assertEqual(metrics.missing_values, 1)
        self.assertEqual(metrics.outliers_removed, 1)
        self.assertEqual(metrics.data_quality_score, 0.8)


class TestPipelineMetrics(unittest.TestCase):
    def test_pipeline_metrics_creation(self):
        metrics = PipelineMetrics.create_empty("test_pipeline")
        
        self.assertEqual(metrics.pipeline_name, "test_pipeline")
        self.assertEqual(metrics.status, "running")
        self.assertEqual(metrics.execution_time, 0.0)
        self.assertEqual(len(metrics.errors), 0)
        self.assertEqual(len(metrics.warnings), 0)
    
    def test_pipeline_metrics_error_handling(self):
        metrics = PipelineMetrics.create_empty()
        
        metrics.add_error("Test error")
        self.assertEqual(len(metrics.errors), 1)
        self.assertEqual(metrics.status, "failure")
        
        metrics.add_warning("Test warning")
        self.assertEqual(len(metrics.warnings), 1)
    
    def test_pipeline_metrics_completion(self):
        metrics = PipelineMetrics.create_empty()
        
        metrics.complete_successfully(10.5, 5)
        self.assertEqual(metrics.execution_time, 10.5)
        self.assertEqual(metrics.files_processed, 5)
        self.assertEqual(metrics.status, "success")


class TestMetricsCollector(unittest.TestCase):
    def test_metrics_collector_workflow(self):
        collector = MetricsCollector()
        
        # Start pipeline
        collector.start_pipeline("test_pipeline")
        self.assertIsNotNone(collector.pipeline_metrics)
        self.assertEqual(collector.pipeline_metrics.status, "running")
        
        # Add error
        collector.add_pipeline_error("Test error")
        self.assertEqual(len(collector.pipeline_metrics.errors), 1)
        
        # Complete pipeline
        collector.complete_pipeline(3)
        self.assertEqual(collector.pipeline_metrics.files_processed, 3)
        
        # Get all metrics
        all_metrics = collector.get_all_metrics()
        self.assertIn('pipeline', all_metrics)


class TestAlertManager(unittest.TestCase):
    def test_alert_creation(self):
        manager = AlertManager()
        
        alert = manager.create_alert(
            title="Test Alert",
            message="This is a test alert",
            severity="high"
        )
        
        self.assertEqual(alert.title, "Test Alert")
        self.assertEqual(alert.severity, "high")
        self.assertEqual(alert.source, "pipeline")
    
    def test_local_alert_logging(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test_alerts.log"
            
            manager = AlertManager()
            alert = manager.create_alert("Test", "Test message")
            
            success = manager.log_alert_locally(alert, str(log_file))
            self.assertTrue(success)
            self.assertTrue(log_file.exists())
            
            # Check log content
            with open(log_file, 'r') as f:
                content = f.read()
                self.assertIn("Test", content)
                self.assertIn("Test message", content)


class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.report_generator = ReportGenerator(self.temp_dir)
    
    def test_report_generation(self):
        # Create sample metrics
        metrics = {
            'pipeline': {
                'status': 'success',
                'execution_time': 10.5,
                'files_processed': 3,
                'errors': [],
                'warnings': []
            },
            'model': {
                'r2_score': 0.85,
                'mse': 100.0,
                'training_samples': 1000
            },
            'data_quality': {
                'data_quality_score': 0.95,
                'total_records': 1000,
                'valid_records': 950
            }
        }
        
        report = self.report_generator.generate_report(metrics)
        
        self.assertEqual(report.pipeline_status, 'success')
        self.assertIsNotNone(report.model_metrics)
        self.assertIsNotNone(report.data_quality_metrics)
        self.assertIsNotNone(report.pipeline_metrics)
        
        # Test summary
        summary = report.summary
        self.assertEqual(summary['status'], 'success')
        self.assertEqual(summary['execution_time'], 10.5)
        self.assertEqual(summary['model_r2_score'], 0.85)
    
    def test_report_saving(self):
        metrics = {
            'pipeline': {'status': 'success', 'execution_time': 5.0}
        }
        
        report = self.report_generator.generate_report(metrics)
        file_path = self.report_generator.save_report(report)
        
        self.assertTrue(Path(file_path).exists())
        
        # Load and verify JSON
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)
            self.assertEqual(loaded_data['pipeline_status'], 'success')
    
    def test_metrics_csv_export(self):
        metrics = {
            'pipeline': {'status': 'success', 'execution_time': 5.0},
            'model': {'r2_score': 0.85, 'mse': 100.0}
        }
        
        self.report_generator.save_metrics_csv(metrics)
        
        csv_file = Path(self.temp_dir) / "metrics" / "metrics_history.csv"
        self.assertTrue(csv_file.exists())
        
        # Check CSV content
        import csv
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertIn('pipeline_status', rows[0])
            self.assertIn('model_r2_score', rows[0])
    
    def test_dashboard_generation(self):
        metrics_history = [
            {
                'pipeline': {'status': 'success', 'execution_time': 5.0, 'timestamp': '2023-01-01T00:00:00'},
                'model': {'r2_score': 0.85}
            },
            {
                'pipeline': {'status': 'success', 'execution_time': 6.0, 'timestamp': '2023-01-02T00:00:00'},
                'model': {'r2_score': 0.87}
            }
        ]
        
        dashboard_data = self.report_generator.generate_dashboard_data(metrics_history)
        
        self.assertEqual(dashboard_data['total_runs'], 2)
        self.assertEqual(dashboard_data['latest_status'], 'success')
        self.assertAlmostEqual(dashboard_data['statistics']['avg_r2_score'], 0.86)
        self.assertEqual(dashboard_data['statistics']['success_rate'], 1.0)
    
    def test_html_dashboard_generation(self):
        dashboard_data = {
            'latest_status': 'success',
            'total_runs': 5,
            'statistics': {
                'success_rate': 0.8,
                'avg_r2_score': 0.85,
                'avg_execution_time': 10.0
            },
            'latest_metrics': {
                'pipeline': {'execution_time': 12.0, 'files_processed': 3},
                'model': {'training_samples': 1000, 'mse': 100.0},
                'data_quality': {'valid_records': 950, 'data_quality_score': 0.95}
            }
        }
        
        html_content = self.report_generator.generate_html_dashboard(dashboard_data)
        
        self.assertIn("Where's My Taxi", html_content)
        self.assertIn("SUCCESS", html_content)
        self.assertIn("80.0%", html_content)  # Success rate
        self.assertIn("0.850", html_content)  # R2 score


if __name__ == '__main__':
    unittest.main()