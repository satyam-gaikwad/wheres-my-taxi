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
    
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        X = X.copy()
        # Remove trips longer than 2 hours
        mask = X['total_sec'] <= 7200
        return X[mask]

# Create preprocessing pipeline
preprocessing = Pipeline([
    ('add_total_sec', Addtotalsec()),
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
    
    # Load and process data
    dfs = []
    for file in data_files:
        df = pd.read_parquet(file)
        dfs.append(df)
    
    data = pd.concat(dfs, ignore_index=True)
    
    # Prepare features and target
    X = preprocessing.fit_transform(data)
    y = data['total_sec'].values
    
    # Train model
    model = SGDRegressor(random_state=42)
    model.fit(X, y)
    
    # Save trained files
    save_trained_files(set(data_files))
    
    return model, X, y 