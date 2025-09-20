# Wheres My Taxi

A Python project for training a machine learning pipeline on taxi trip data.

## Directory Structure

```
wheres-my-taxi/
├── wheres_my_taxi/
│   ├── __init__.py
│   ├── pipeline.py         # (main pipeline logic)
│   └── check_new_data_test.py  # (checks for new data)
├── scripts/
│   └── run_pipeline.py     # (CLI entry point)
├── tests/
│   └── test_pipeline.py    # (unit tests)
├── data/
│   ├── raw/
│   └── processed/
├── .github/
│   └── workflows/
│       └── ci.yml          # (GitHub Actions workflow)
├── requirements.txt
├── setup.py
└── README.md
```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd wheres-my-taxi
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Running the Pipeline

Run the pipeline using the CLI script:
```bash
python scripts/run_pipeline.py
```

### Retraining

To force retraining on all data, use the `--retrain` flag:
```bash
python scripts/run_pipeline.py --retrain
```

## CI/CD and Monitoring

This project uses GitHub Actions for continuous integration and includes comprehensive monitoring:

### CI/CD Pipeline
- **Automated Testing**: Runs on push/PR to main branches
- **Linting and Code Quality**: flake8, black, isort
- **Pipeline Execution**: Automated ML pipeline runs every 6 hours
- **Artifact Storage**: Monitoring reports and model artifacts

### Monitoring System 🎯
The project includes a comprehensive monitoring system with:
- **Model Performance Tracking**: MSE, R², MAE metrics
- **Data Quality Monitoring**: Validation, missing values, duplicates
- **Pipeline Health**: Execution time, memory usage, error tracking
- **GitHub Integration**: Automated issue creation for failures
- **Real-time Dashboard**: HTML dashboard deployed to GitHub Pages
- **Historical Analysis**: CSV exports and JSON reports

#### Quick Monitoring Setup
```bash
# Set GitHub token (optional, for alerts)
export GITHUB_TOKEN="your_github_token"

# Run pipeline with monitoring
python scripts/run_pipeline.py --retrain

# View monitoring dashboard
open monitoring/reports/dashboard/index.html
```

For detailed monitoring documentation, see [MONITORING.md](MONITORING.md).

### GitHub Actions Workflow
The workflow includes:
- Linting with flake8
- Running the ML pipeline with monitoring
- Automated testing with coverage
- Dashboard deployment to GitHub Pages
- Monitoring artifact uploads

## License

[Your License Here] 