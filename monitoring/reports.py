"""
Reporting system for the Where's My Taxi ML pipeline.

This module provides GitHub-based reporting capabilities including:
- Generating monitoring reports
- Creating GitHub Pages dashboard data
- Storing metrics artifacts
"""

import os
import json
import csv
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


@dataclass
class MonitoringReport:
    """Monitoring report data structure."""
    timestamp: str
    pipeline_status: str
    model_metrics: Optional[Dict[str, Any]]
    data_quality_metrics: Optional[Dict[str, Any]]
    pipeline_metrics: Optional[Dict[str, Any]]
    summary: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, cls=NumpyEncoder)


class ReportGenerator:
    """Generate monitoring reports and dashboards."""
    
    def __init__(self, reports_dir: str = "monitoring/reports"):
        """Initialize report generator."""
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.reports_dir / "metrics").mkdir(exist_ok=True)
        (self.reports_dir / "dashboard").mkdir(exist_ok=True)
    
    def generate_report(self, metrics: Dict[str, Any]) -> MonitoringReport:
        """
        Generate monitoring report from metrics.
        
        Args:
            metrics: Dictionary containing all metrics
            
        Returns:
            MonitoringReport: Generated report
        """
        # Extract metrics
        pipeline_metrics = metrics.get('pipeline', {})
        model_metrics = metrics.get('model', {})
        data_quality_metrics = metrics.get('data_quality', {})
        
        # Determine overall status
        pipeline_status = pipeline_metrics.get('status', 'unknown')
        
        # Generate summary
        summary = self._generate_summary(pipeline_metrics, model_metrics, data_quality_metrics)
        
        return MonitoringReport(
            timestamp=datetime.utcnow().isoformat(),
            pipeline_status=pipeline_status,
            model_metrics=model_metrics if model_metrics else None,
            data_quality_metrics=data_quality_metrics if data_quality_metrics else None,
            pipeline_metrics=pipeline_metrics if pipeline_metrics else None,
            summary=summary
        )
    
    def _generate_summary(self, pipeline_metrics: Dict, model_metrics: Dict, 
                         data_quality_metrics: Dict) -> Dict[str, Any]:
        """Generate summary statistics."""
        summary = {
            'status': pipeline_metrics.get('status', 'unknown'),
            'execution_time': pipeline_metrics.get('execution_time', 0),
            'files_processed': pipeline_metrics.get('files_processed', 0),
            'error_count': len(pipeline_metrics.get('errors', [])),
            'warning_count': len(pipeline_metrics.get('warnings', []))
        }
        
        # Add model summary if available
        if model_metrics:
            summary.update({
                'model_r2_score': model_metrics.get('r2_score', 0),
                'model_mse': model_metrics.get('mse', 0),
                'training_samples': model_metrics.get('training_samples', 0)
            })
        
        # Add data quality summary if available
        if data_quality_metrics:
            summary.update({
                'data_quality_score': data_quality_metrics.get('data_quality_score', 0),
                'total_records': data_quality_metrics.get('total_records', 0),
                'valid_records': data_quality_metrics.get('valid_records', 0)
            })
        
        return summary
    
    def save_report(self, report: MonitoringReport, filename: Optional[str] = None) -> str:
        """
        Save monitoring report to file.
        
        Args:
            report: Report to save
            filename: Optional filename, defaults to timestamp-based name
            
        Returns:
            str: Path to saved file
        """
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.json"
        
        filepath = self.reports_dir / "metrics" / filename
        
        with open(filepath, 'w') as f:
            f.write(report.to_json())
        
        return str(filepath)
    
    def save_metrics_csv(self, metrics: Dict[str, Any], filename: str = "metrics_history.csv"):
        """
        Save metrics to CSV file for historical tracking.
        
        Args:
            metrics: Metrics dictionary
            filename: CSV filename
        """
        filepath = self.reports_dir / "metrics" / filename
        
        # Flatten metrics for CSV
        flattened = self._flatten_metrics(metrics)
        
        # Check if file exists to determine if we need headers
        file_exists = filepath.exists()
        
        with open(filepath, 'a', newline='') as f:
            if flattened:
                writer = csv.DictWriter(f, fieldnames=flattened.keys())
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(flattened)
    
    def _flatten_metrics(self, metrics: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested metrics dictionary for CSV export."""
        flattened = {}
        
        for key, value in metrics.items():
            new_key = f"{prefix}{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_metrics(value, f"{new_key}_"))
            elif isinstance(value, list):
                # Convert lists to comma-separated strings
                flattened[new_key] = ",".join(str(item) for item in value)
            else:
                flattened[new_key] = value
        
        return flattened
    
    def generate_dashboard_data(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate dashboard data from metrics history.
        
        Args:
            metrics_history: List of historical metrics
            
        Returns:
            Dict containing dashboard data
        """
        if not metrics_history:
            return {}
        
        # Extract time series data
        timestamps = []
        r2_scores = []
        execution_times = []
        data_quality_scores = []
        
        for metrics in metrics_history:
            pipeline_metrics = metrics.get('pipeline', {})
            model_metrics = metrics.get('model', {})
            data_metrics = metrics.get('data_quality', {})
            
            timestamp = pipeline_metrics.get('timestamp')
            if timestamp:
                timestamps.append(timestamp)
                r2_scores.append(model_metrics.get('r2_score', 0))
                execution_times.append(pipeline_metrics.get('execution_time', 0))
                data_quality_scores.append(data_metrics.get('data_quality_score', 0))
        
        # Calculate statistics
        latest_metrics = metrics_history[-1] if metrics_history else {}
        
        dashboard_data = {
            'last_updated': datetime.utcnow().isoformat(),
            'total_runs': len(metrics_history),
            'latest_status': latest_metrics.get('pipeline', {}).get('status', 'unknown'),
            'time_series': {
                'timestamps': timestamps,
                'r2_scores': r2_scores,
                'execution_times': execution_times,
                'data_quality_scores': data_quality_scores
            },
            'statistics': {
                'avg_r2_score': sum(r2_scores) / len(r2_scores) if r2_scores else 0,
                'avg_execution_time': sum(execution_times) / len(execution_times) if execution_times else 0,
                'avg_data_quality': sum(data_quality_scores) / len(data_quality_scores) if data_quality_scores else 0,
                'success_rate': sum(1 for m in metrics_history if m.get('pipeline', {}).get('status') == 'success') / len(metrics_history) if metrics_history else 0
            },
            'latest_metrics': latest_metrics
        }
        
        return dashboard_data
    
    def save_dashboard_data(self, dashboard_data: Dict[str, Any], 
                          filename: str = "dashboard_data.json") -> str:
        """
        Save dashboard data for GitHub Pages.
        
        Args:
            dashboard_data: Dashboard data dictionary
            filename: JSON filename
            
        Returns:
            str: Path to saved file
        """
        filepath = self.reports_dir / "dashboard" / filename
        
        with open(filepath, 'w') as f:
            json.dump(dashboard_data, f, indent=2, cls=NumpyEncoder)
        
        return str(filepath)
    
    def generate_html_dashboard(self, dashboard_data: Dict[str, Any]) -> str:
        """
        Generate HTML dashboard for GitHub Pages.
        
        Args:
            dashboard_data: Dashboard data
            
        Returns:
            str: HTML content
        """
        latest_metrics = dashboard_data.get('latest_metrics', {})
        pipeline_metrics = latest_metrics.get('pipeline', {})
        model_metrics = latest_metrics.get('model', {})
        data_metrics = latest_metrics.get('data_quality', {})
        stats = dashboard_data.get('statistics', {})
        
        # Status color
        status = dashboard_data.get('latest_status', 'unknown')
        status_color = {
            'success': '#28a745',
            'failure': '#dc3545',
            'warning': '#ffc107',
            'unknown': '#6c757d'
        }.get(status, '#6c757d')
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Where's My Taxi - ML Pipeline Monitoring</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            background-color: {status_color};
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}
        .metric-title {{
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            text-align: center;
            margin-top: 20px;
        }}
        .error-list {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
        }}
        .warning-list {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Where's My Taxi - ML Pipeline Monitoring</h1>
            <div class="status-badge">{status.upper()}</div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">Total Pipeline Runs</div>
                <div class="metric-value">{dashboard_data.get('total_runs', 0)}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Success Rate</div>
                <div class="metric-value">{stats.get('success_rate', 0):.1%}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Average R² Score</div>
                <div class="metric-value">{stats.get('avg_r2_score', 0):.3f}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Average Execution Time</div>
                <div class="metric-value">{stats.get('avg_execution_time', 0):.1f}s</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Average Data Quality</div>
                <div class="metric-value">{stats.get('avg_data_quality', 0):.1%}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Latest Execution Time</div>
                <div class="metric-value">{pipeline_metrics.get('execution_time', 0):.1f}s</div>
            </div>
        </div>
        
        <h2>Latest Pipeline Run</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">Files Processed</div>
                <div class="metric-value">{pipeline_metrics.get('files_processed', 0)}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Memory Usage</div>
                <div class="metric-value">{pipeline_metrics.get('memory_usage_mb', 0):.1f} MB</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Training Samples</div>
                <div class="metric-value">{model_metrics.get('training_samples', 0):,}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Model MSE</div>
                <div class="metric-value">{model_metrics.get('mse', 0):.2f}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Valid Records</div>
                <div class="metric-value">{data_metrics.get('valid_records', 0):,}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Data Quality Score</div>
                <div class="metric-value">{data_metrics.get('data_quality_score', 0):.1%}</div>
            </div>
        </div>
"""
        
        # Add errors if any
        errors = pipeline_metrics.get('errors', [])
        if errors:
            html += """
        <h2>Recent Errors</h2>
        <div class="error-list">
            <ul>
"""
            for error in errors:
                html += f"                <li>{error}</li>\n"
            html += """
            </ul>
        </div>
"""
        
        # Add warnings if any
        warnings = pipeline_metrics.get('warnings', [])
        if warnings:
            html += """
        <h2>Recent Warnings</h2>
        <div class="warning-list">
            <ul>
"""
            for warning in warnings:
                html += f"                <li>{warning}</li>\n"
            html += """
            </ul>
        </div>
"""
        
        html += f"""
        <div class="timestamp">
            Last updated: {dashboard_data.get('last_updated', 'Unknown')}
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def save_html_dashboard(self, dashboard_data: Dict[str, Any], 
                          filename: str = "index.html") -> str:
        """
        Save HTML dashboard for GitHub Pages.
        
        Args:
            dashboard_data: Dashboard data
            filename: HTML filename
            
        Returns:
            str: Path to saved file
        """
        html_content = self.generate_html_dashboard(dashboard_data)
        filepath = self.reports_dir / "dashboard" / filename
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def load_metrics_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Load metrics history from saved reports.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of metrics dictionaries
        """
        metrics_dir = self.reports_dir / "metrics"
        if not metrics_dir.exists():
            return []
        
        history = []
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Load all JSON reports
        for report_file in metrics_dir.glob("report_*.json"):
            try:
                with open(report_file, 'r') as f:
                    report_data = json.load(f)
                
                # Check if report is within date range
                timestamp_str = report_data.get('timestamp', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if timestamp >= cutoff_date:
                        # Extract metrics from report
                        metrics = {
                            'pipeline': report_data.get('pipeline_metrics'),
                            'model': report_data.get('model_metrics'),
                            'data_quality': report_data.get('data_quality_metrics')
                        }
                        history.append(metrics)
                        
            except Exception as e:
                print(f"Error loading report {report_file}: {e}")
                continue
        
        # Sort by timestamp
        history.sort(key=lambda x: x.get('pipeline', {}).get('timestamp', ''))
        
        return history