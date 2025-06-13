import unittest
import pandas as pd
import numpy as np
from test.utils.data_validation import (
    validate_data, validate_processed_data, validate_training_data
)

class TestDataValidation(unittest.TestCase):
    def test_validate_data(self):
        # Test raw data validation
        data = pd.DataFrame({
            'PULocationID': [1, 2, 3],
            'DOLocationID': [1, 2, 3],
            'tpep_pickup_datetime': pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-01']),
            'tpep_dropoff_datetime': pd.to_datetime(['2023-01-01 00:01:00', '2023-01-01 00:01:00', '2023-01-01 00:01:00']),
            'trip_distance': [1, 1, 1],
            'fare_amount': [1, 1, 1],
            'total_amount': [1, 1, 1]
        })
        is_valid, message = validate_data(data)
        self.assertTrue(is_valid)
        self.assertEqual(message, "Data validation passed")

    def test_validate_processed_data(self):
        # Test processed data validation
        data = pd.DataFrame({
            'PULocationID': [1, 2, 3],
            'DOLocationID': [1, 2, 3],
            'tpep_pickup_datetime': pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-01']),
            'tpep_dropoff_datetime': pd.to_datetime(['2023-01-01 00:01:00', '2023-01-01 00:01:00', '2023-01-01 00:01:00']),
            'trip_distance': [1, 1, 1],
            'fare_amount': [1, 1, 1],
            'total_amount': [1, 1, 1],
            'total_sec': [60, 60, 60],
            'day_number': [1, 1, 1],
            'PU_hour': [0, 0, 0]
        })
        is_valid, message = validate_processed_data(data)
        self.assertTrue(is_valid)
        self.assertEqual(message, "Processed data validation passed")

    def test_validate_training_data(self):
        # Test training data validation
        X = np.array([[1, 2, 3], [4, 5, 6]])
        y = np.array([1, 2])
        is_valid, message = validate_training_data(X, y)
        self.assertTrue(is_valid)
        self.assertEqual(message, "Training data validation passed")

    def test_invalid_data(self):
        # Test invalid data scenarios
        # Missing required columns
        data = pd.DataFrame({'A': [1, 2, 3]})
        is_valid, message = validate_data(data)
        self.assertFalse(is_valid)
        self.assertIn("Missing required columns", message)

        # Invalid data types
        data = pd.DataFrame({
            'PULocationID': ['a', 'b', 'c'],  # Should be numeric
            'DOLocationID': [1, 2, 3],
            'tpep_pickup_datetime': pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-01']),
            'tpep_dropoff_datetime': pd.to_datetime(['2023-01-01 00:01:00', '2023-01-01 00:01:00', '2023-01-01 00:01:00']),
            'trip_distance': [1, 1, 1],
            'fare_amount': [1, 1, 1],
            'total_amount': [1, 1, 1]
        })
        is_valid, message = validate_data(data)
        self.assertFalse(is_valid)
        self.assertIn("Invalid data types", message)

if __name__ == '__main__':
    unittest.main() 