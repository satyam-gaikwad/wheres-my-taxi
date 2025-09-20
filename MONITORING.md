# Monitoring System Documentation

## Overview

The Where's My Taxi ML pipeline includes a comprehensive monitoring system that leverages GitHub-native tools and third-party integrations for real-time pipeline health, model performance, and data quality monitoring.

## Features

### 🎯 Core Monitoring Capabilities

- **Model Performance Tracking**: MSE, R², MAE, training duration, and sample counts
- **Data Quality Monitoring**: Record validation, missing values, duplicates, and quality scores
- **Pipeline Health Monitoring**: Execution time, memory usage, CPU usage, error tracking
- **GitHub-Based Alerting**: Automatic issue creation for failures and performance degradation
- **Dashboard Generation**: HTML dashboard with real-time metrics and historical trends
- **Historical Tracking**: CSV export and JSON reports for long-term analysis

### 🔧 GitHub Integration

- **GitHub Issues API**: Automated alerting for failures and quality issues
- **GitHub Actions Artifacts**: Metric storage and historical tracking
- **GitHub Pages**: Static monitoring dashboard deployment
- **GitHub API**: Pipeline status and performance reporting
- **Workflow Status Updates**: Real-time commit status updates

## Quick Start

### 1. Environment Setup

```bash
# Install monitoring dependencies
pip install requests PyGithub psutil

# Set environment variables (optional for GitHub integration)
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPOSITORY="owner/repo"
```

### 2. Basic Usage

```python
from monitoring.metrics import MetricsCollector
from monitoring.alerts import AlertManager
from monitoring.reports import ReportGenerator

# Initialize monitoring components
metrics_collector = MetricsCollector()
alert_manager = AlertManager()
report_generator = ReportGenerator()

# Start pipeline monitoring
metrics_collector.start_pipeline("my_pipeline")

# ... your pipeline code ...

# Collect model metrics
metrics_collector.collect_model_metrics(model, X, y)

# Complete and generate report
metrics_collector.complete_pipeline(files_processed=5)
all_metrics = metrics_collector.get_all_metrics()
report = report_generator.generate_report(all_metrics)
```

### 3. Integration with Pipeline

The monitoring system is already integrated into the main pipeline script (`scripts/run_pipeline.py`). Simply run:

```bash
python scripts/run_pipeline.py --retrain
```

## Monitoring Components

### 📊 Metrics Collection

#### ModelMetrics
- **MSE (Mean Squared Error)**: Model prediction accuracy
- **R² Score**: Coefficient of determination
- **MAE (Mean Absolute Error)**: Average prediction error
- **Training Duration**: Time taken to train the model
- **Sample Count**: Number of training samples
- **Feature Count**: Number of input features

#### DataQualityMetrics
- **Total Records**: Original dataset size
- **Valid Records**: Records passing validation
- **Invalid Records**: Records filtered out
- **Missing Values**: Count of null/missing values
- **Duplicate Records**: Count of duplicate entries
- **Data Quality Score**: Percentage of valid records

#### PipelineMetrics
- **Execution Time**: Total pipeline runtime
- **Memory Usage**: Peak memory consumption
- **CPU Usage**: CPU utilization percentage
- **Files Processed**: Number of data files processed
- **Error Count**: Number of errors encountered
- **Warning Count**: Number of warnings generated

### 🚨 Alerting System

#### GitHub Issues Integration
- Automatic issue creation for pipeline failures
- Performance degradation alerts
- Data quality threshold violations
- Configurable severity levels (critical, high, medium, low)

#### Alert Types
- **Pipeline Failure**: Critical errors that stop execution
- **Model Performance**: R² score below threshold (default: 0.5)
- **Data Quality**: Quality score below threshold (default: 0.8)

### 📈 Reporting and Dashboard

#### Reports
- **JSON Reports**: Detailed metrics in machine-readable format
- **CSV Export**: Historical data for analysis
- **HTML Dashboard**: Real-time monitoring interface

#### Dashboard Features
- **Status Overview**: Current pipeline health
- **Performance Metrics**: Model accuracy trends
- **System Resources**: Memory and CPU usage
- **Historical Trends**: Performance over time
- **Error Tracking**: Recent errors and warnings

## Configuration

### GitHub Token Setup

For full GitHub integration, create a personal access token with the following permissions:
- `repo` (for issue creation and status updates)
- `workflow` (for GitHub Actions integration)

### Alert Thresholds

Configure alert thresholds in your pipeline:

```python
# Model performance threshold (R² score)
alert_manager.send_model_performance_alert(metrics, threshold_r2=0.6)

# Data quality threshold
alert_manager.send_data_quality_alert(metrics, quality_threshold=0.85)
```

### Dashboard Customization

Customize the dashboard by modifying `monitoring/reports.py`:

```python
# Generate custom dashboard
dashboard_data = report_generator.generate_dashboard_data(metrics_history)
html_dashboard = report_generator.generate_html_dashboard(dashboard_data)
```

## GitHub Actions Integration

The monitoring system includes enhanced GitHub Actions workflows:

### Workflow Features
- **Automated Pipeline Runs**: Scheduled execution every 6 hours
- **Monitoring Artifacts**: Upload reports and logs
- **GitHub Pages Deployment**: Automatic dashboard deployment
- **Status Updates**: Commit status updates with pipeline results

### Workflow Configuration

```yaml
# .github/workflows/pipeline_test.yml
name: ML Pipeline Monitoring and CI

on:
  workflow_dispatch:
  push:
    branches: [ main, master ]
  schedule:
    - cron: '0 */6 * * *'  # Run every 6 hours

jobs:
  pipeline-monitoring:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pages: write
```

## File Structure

```
monitoring/
├── __init__.py              # Module exports
├── metrics.py               # Metrics collection classes
├── alerts.py                # GitHub-based alerting
├── reports.py               # Report generation and dashboard
├── logger.py                # Structured logging
├── logs/                    # Log files
│   └── monitoring.log
└── reports/                 # Generated reports
    ├── metrics/             # JSON reports and CSV data
    │   ├── report_*.json
    │   └── metrics_history.csv
    └── dashboard/           # Dashboard files
        ├── index.html
        └── dashboard_data.json
```

## API Reference

### MetricsCollector

```python
class MetricsCollector:
    def start_pipeline(pipeline_name: str)
    def collect_model_metrics(model, X, y, model_type: str)
    def collect_data_quality_metrics(original_data, processed_data, outliers_removed: int)
    def complete_pipeline(files_processed: int)
    def add_pipeline_error(error: str)
    def add_pipeline_warning(warning: str)
    def get_all_metrics() -> Dict[str, Any]
```

### AlertManager

```python
class AlertManager:
    def __init__(github_token: str, repo_name: str)
    def send_pipeline_failure_alert(error_message: str, metrics: Dict)
    def send_model_performance_alert(metrics: Dict, threshold_r2: float)
    def send_data_quality_alert(metrics: Dict, quality_threshold: float)
    def send_workflow_status_update(status: str, metrics: Dict)
```

### ReportGenerator

```python
class ReportGenerator:
    def __init__(reports_dir: str)
    def generate_report(metrics: Dict) -> MonitoringReport
    def save_report(report: MonitoringReport) -> str
    def save_metrics_csv(metrics: Dict)
    def generate_dashboard_data(metrics_history: List) -> Dict
    def save_html_dashboard(dashboard_data: Dict) -> str
```

## Best Practices

### 1. Error Handling
- Always wrap monitoring calls in try-catch blocks
- Provide fallback mechanisms for GitHub API failures
- Log monitoring errors separately from pipeline errors

### 2. Performance
- Collect metrics incrementally during pipeline execution
- Use sampling for large datasets in data quality metrics
- Limit historical data retention (default: 30 days)

### 3. Security
- Store GitHub tokens as environment variables or secrets
- Avoid logging sensitive data in monitoring reports
- Use appropriate GitHub permissions (minimal required scope)

### 4. Maintenance
- Regularly review and close resolved GitHub issues
- Archive old monitoring reports
- Monitor monitoring system resource usage

## Troubleshooting

### Common Issues

#### GitHub Token Issues
```
Warning: GitHub repository not available for issue creation
```
**Solution**: Set `GITHUB_TOKEN` environment variable with proper permissions.

#### JSON Serialization Errors
```
TypeError: Object of type int64 is not JSON serializable
```
**Solution**: Use the built-in `NumpyEncoder` for handling numpy types.

#### Missing Dependencies
```
ImportError: No module named 'github'
```
**Solution**: Install PyGithub with `pip install PyGithub`.

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Local Testing

Test monitoring without GitHub integration:

```python
# Disable GitHub features for local testing
alert_manager = AlertManager(github_token=None)
```

## Examples

See `tests/test_monitoring.py` for comprehensive usage examples and test cases.

## Contributing

1. Add new metrics by extending the metrics classes
2. Implement new alert types in `alerts.py`
3. Customize dashboard templates in `reports.py`
4. Add tests for new functionality
5. Update documentation