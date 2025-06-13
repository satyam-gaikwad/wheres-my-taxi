import unittest
import pandas as pd
import numpy as np
from test.utils.pipeline import (
    ColumnSelector, DropInvalidRows, AddDayNumber, AddPUhour, Addtotalsec, RemoveOutliers,
    preprocessing, train_sgd_regressor, get_trained_files, save_trained_files
)
from test.utils.check_new_data_test import check_new_data

class TestPipeline(unittest.TestCase):
    def test_column_selector(self):
        # Test ColumnSelector
        data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        selector = ColumnSelector(columns=['A'])
        result = selector.transform(data)
        self.assertEqual(list(result.columns), ['A'])

    def test_drop_invalid_rows(self):
        # Test DropInvalidRows
        data = pd.DataFrame({
            'PULocationID': [0, 264, 1],
            'DOLocationID': [0, 264, 1],
            'tpep_pickup_datetime': pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-01']),
            'trip_distance': [0, 1, 1],
            'fare_amount': [0, 1, 1],
            'total_amount': [0, 1, 1],
            'total_sec': [0, 1, 1]
        })
        transformer = DropInvalidRows()
        result = transformer.transform(data)
        self.assertEqual(len(result), 1)  # Only one valid row

    def test_preprocessing_pipeline(self):
        # Test the full preprocessing pipeline
        data = pd.DataFrame({
            'PULocationID': [1, 2, 3],
            'DOLocationID': [1, 2, 3],
            'tpep_pickup_datetime': pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-01']),
            'tpep_dropoff_datetime': pd.to_datetime(['2023-01-01 00:01:00', '2023-01-01 00:01:00', '2023-01-01 00:01:00']),
            'trip_distance': [1, 1, 1],
            'fare_amount': [1, 1, 1],
            'total_amount': [1, 1, 1],
            'total_sec': [1, 1, 1]
        })
        result = preprocessing.fit_transform(data)
        self.assertIsInstance(result, np.ndarray)

    def test_train_sgd_regressor(self):
        # Test the training function
        data_files = ['dummy_file.parquet']  # Mock file
        num_files = 1
        sgd, x_test, y_test = train_sgd_regressor(data_files, num_files)
        self.assertIsNotNone(sgd)

    def test_check_new_data(self):
        # Test the new data detection
        new_files = check_new_data()
        self.assertIsInstance(new_files, list)

    def test_get_and_save_trained_files(self):
        # Test file tracking
        files = {'file1.parquet', 'file2.parquet'}
        save_trained_files(files)
        loaded_files = get_trained_files()
        self.assertEqual(loaded_files, files)

if __name__ == '__main__':
    unittest.main() 