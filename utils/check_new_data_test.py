import os
from pathlib import Path
from typing import List, Set
from .utils import get_processed_files, get_trained_files

def get_all_data_files() -> List[str]:
    """
    Get all data files from both raw and processed directories.
    
    Returns:
        List of paths to all data files
    """
    data_dir = Path(__file__).parent.parent / "data"
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    
    all_files = []
    
    # Get files from raw directory
    if raw_dir.exists():
        raw_files = sorted(raw_dir.glob("*.parquet"))
        all_files.extend([str(f) for f in raw_files])
    
    # Get files from processed directory
    if processed_dir.exists():
        processed_files = sorted(processed_dir.glob("*.parquet"))
        all_files.extend([str(f) for f in processed_files])
    
    return sorted(all_files)

def check_new_data() -> List[str]:
    """
    Check for new data files in the data directory.
    
    Returns:
        List of paths to new data files
    """
    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return []
        
    # Get all parquet files
    data_files = sorted(data_dir.glob("*.parquet"))
    if not data_files:
        print("No data files found.")
        return []
        
    return [str(f) for f in data_files]

def get_unprocessed_files() -> List[str]:
    """
    Get list of files that haven't been processed yet.
    
    Returns:
        List of unprocessed file paths
    """
    return check_new_data()

def get_untrained_files() -> List[str]:
    """
    Get list of processed files that haven't been used for training.
    
    Returns:
        List of untrained file paths
    """
    processed_files = get_processed_files()
    trained_files = get_trained_files()
    
    # Find files that are processed but not trained
    untrained_files = processed_files - trained_files
    
    # Convert to full paths
    processed_dir = Path("data/processed")
    untrained_file_paths = [str(processed_dir / f) for f in untrained_files]
    
    return untrained_file_paths 