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

## CI/CD

This project uses GitHub Actions for continuous integration. The workflow includes:
- Linting with flake8
- Running the pipeline
- Running tests

## License

[Your License Here] 