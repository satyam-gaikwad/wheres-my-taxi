import pandas as pd
import numpy as np
from typing import Tuple, List

def validate_data(data: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate raw data format and content.
    
    Args:
        data: Raw taxi trip data
        
    Returns:
        Tuple of (is_valid, message)
    """
    required_columns = [
        'PULocationID', 'DOLocationID', 'tpep_pickup_datetime',
        'tpep_dropoff_datetime', 'trip_distance', 'fare_amount',
        'total_amount'
    ]
    
    # Check required columns
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check data types
    try:
        # Check numeric columns
        numeric_columns = ['PULocationID', 'DOLocationID', 'trip_distance', 
                         'fare_amount', 'total_amount']
        for col in numeric_columns:
            pd.to_numeric(data[col])
            
        # Check datetime columns
        pd.to_datetime(data['tpep_pickup_datetime'])
        pd.to_datetime(data['tpep_dropoff_datetime'])
        
    except Exception as e:
        return False, f"Invalid data types: {str(e)}"
    
    return True, "Data validation passed"

def validate_processed_data(data: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate processed data format and content.
    
    Args:
        data: Processed taxi trip data
        
    Returns:
        Tuple of (is_valid, message)
    """
    required_columns = [
        'PULocationID', 'DOLocationID', 'tpep_pickup_datetime',
        'tpep_dropoff_datetime', 'trip_distance', 'fare_amount',
        'total_amount', 'total_sec', 'day_number', 'PU_hour'
    ]
    
    # Check required columns
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check data types
    try:
        # Check numeric columns
        numeric_columns = ['PULocationID', 'DOLocationID', 'trip_distance', 
                         'fare_amount', 'total_amount', 'total_sec',
                         'day_number', 'PU_hour']
        for col in numeric_columns:
            pd.to_numeric(data[col])
            
        # Check datetime columns
        pd.to_datetime(data['tpep_pickup_datetime'])
        pd.to_datetime(data['tpep_dropoff_datetime'])
        
    except Exception as e:
        return False, f"Invalid data types: {str(e)}"
    
    return True, "Processed data validation passed"

def validate_training_data(X: np.ndarray, y: np.ndarray) -> Tuple[bool, str]:
    """
    Validate training data format and content.
    
    Args:
        X: Feature matrix
        y: Target vector
        
    Returns:
        Tuple of (is_valid, message)
    """
    # Check shapes
    if len(X) != len(y):
        return False, "Feature matrix and target vector have different lengths"
    
    # Check for NaN values
    if np.isnan(X).any() or np.isnan(y).any():
        return False, "Data contains NaN values"
    
    # Check for infinite values
    if np.isinf(X).any() or np.isinf(y).any():
        return False, "Data contains infinite values"
    
    return True, "Training data validation passed" 