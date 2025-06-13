import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDRegressor
from typing import List, Tuple, Set
from .utils import get_trained_files, save_trained_files

class ColumnSelector(BaseEstimator, TransformerMixin):
    """Select specific columns from the dataframe."""
    
    def __init__(self, columns: List[str]):
        self.columns = columns
        
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        return X[self.columns]

class DropInvalidRows(BaseEstimator, TransformerMixin):
    """Drop rows with invalid values."""
    
    def __init__(self):
        self.dropped_indices_ = None
        
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        # Drop rows with invalid location IDs
        mask = (X['PULocationID'] > 0) & (X['PULocationID'] < 264) & \
               (X['DOLocationID'] > 0) & (X['DOLocationID'] < 264)
        
        # Drop rows with invalid trip metrics
        mask &= (X['trip_distance'] > 0) & \
                (X['fare_amount'] > 0) & \
                (X['total_amount'] > 0) & \
                (X['total_sec'] > 0)
        
        # Store dropped indices
        self.dropped_indices_ = X.index[~mask]
        
        return X[mask]

class AddDayNumber(BaseEstimator, TransformerMixin):
    """Add day number feature."""
    
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        X = X.copy()
        X['day_number'] = pd.to_datetime(X['tpep_pickup_datetime']).dt.dayofweek
        return X

class AddPUhour(BaseEstimator, TransformerMixin):
    """Add pickup hour feature."""
    
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        X = X.copy()
        X['PU_hour'] = pd.to_datetime(X['tpep_pickup_datetime']).dt.hour
        return X

class Addtotalsec(BaseEstimator, TransformerMixin):
    """Add total seconds feature."""
    
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        X = X.copy()
        pickup = pd.to_datetime(X['tpep_pickup_datetime'])
        dropoff = pd.to_datetime(X['tpep_dropoff_datetime'])
        X['total_sec'] = (dropoff - pickup).dt.total_seconds()
        return X

class RemoveOutliers(BaseEstimator, TransformerMixin):
    """Remove outliers based on total seconds."""
    
    def __init__(self):
        self.dropped_indices_ = None
        
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        X = X.copy()
        # Remove trips longer than 2 hours
        mask = X['total_sec'] <= 7200
        self.dropped_indices_ = X.index[~mask]
        return X[mask]

# Create preprocessing pipeline
preprocessing = Pipeline([
    ('add_day_number', AddDayNumber()),
    ('add_pu_hour', AddPUhour()),
    ('remove_outliers', RemoveOutliers()),
    ('drop_invalid', DropInvalidRows()),
    ('select_features', ColumnSelector([
        'PULocationID', 'DOLocationID', 'trip_distance',
        'day_number', 'PU_hour'
    ])),
    ('scaler', StandardScaler())
])

def train_sgd_regressor(data_files: List[str], num_files: int = None) -> Tuple[SGDRegressor, np.ndarray, np.ndarray]:
    """
    Train SGD regressor on processed data.
    
    Args:
        data_files: List of data file paths
        num_files: Number of files to use (None for all)
        
    Returns:
        Tuple of (model, X_test, y_test)
    """
    if num_files is not None:
        data_files = data_files[:num_files]
    
    if not data_files:
        print("No files provided for training.")
        return None, None, None
    
    print(f"Processing {len(data_files)} files...")
    
    # Load and process data
    dfs = []
    valid_files = []
    for file in data_files:
        try:
            df = pd.read_parquet(file)
            # Calculate total_sec before preprocessing
            pickup = pd.to_datetime(df['tpep_pickup_datetime'])
            dropoff = pd.to_datetime(df['tpep_dropoff_datetime'])
            df['total_sec'] = (dropoff - pickup).dt.total_seconds()
            dfs.append(df)
            valid_files.append(file)
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
            continue
    
    if not dfs:
        print("No valid data files to process.")
        return None, None, None
    
    data = pd.concat(dfs, ignore_index=True)
    
    # Store target before preprocessing
    y = data['total_sec'].values
    
    # Prepare features
    X = preprocessing.fit_transform(data)
    
    # Get all dropped indices from preprocessing steps
    dropped_indices = set()
    if hasattr(preprocessing.named_steps['remove_outliers'], 'dropped_indices_'):
        dropped_indices.update(preprocessing.named_steps['remove_outliers'].dropped_indices_)
    if hasattr(preprocessing.named_steps['drop_invalid'], 'dropped_indices_'):
        dropped_indices.update(preprocessing.named_steps['drop_invalid'].dropped_indices_)
    
    # Filter y to match X
    mask = ~data.index.isin(dropped_indices)
    y = y[mask]
    
    # Verify shapes match
    assert len(X) == len(y), f"X shape {len(X)} != y shape {len(y)}"
    
    # Train model
    model = SGDRegressor(random_state=42)
    model.fit(X, y)
    
    # Save only the successfully processed files as trained
    if valid_files:
        save_trained_files(set(valid_files))
        print(f"Successfully processed and saved {len(valid_files)} files as trained.")
    
    return model, X, y 