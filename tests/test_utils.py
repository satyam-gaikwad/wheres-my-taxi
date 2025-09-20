import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.utils import (
    get_processed_files, get_trained_files, save_trained_files,
    save_processed_files
)

class TestUtils(unittest.TestCase):
    def test_file_tracking(self):
        # Test file tracking functions
        test_files = {'file1.parquet', 'file2.parquet'}
        
        # Test save and get trained files
        save_trained_files(test_files)
        loaded_files = get_trained_files()
        self.assertEqual(loaded_files, test_files)
        
        # Test save and get processed files
        save_processed_files(test_files)
        loaded_files = get_processed_files()
        self.assertEqual(loaded_files, test_files)

    def test_file_operations(self):
        # Test file operations with empty sets
        empty_set = set()
        save_trained_files(empty_set)
        loaded_files = get_trained_files()
        self.assertEqual(loaded_files, empty_set)

if __name__ == '__main__':
    unittest.main() 