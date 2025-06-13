import os
from pathlib import Path
from typing import List, Set
from .utils import get_processed_files, get_trained_files

def check_new_data() -> List[str]:
    """
    Check for new data files that haven't been processed or trained on.
    
    Returns:
        List of new file paths
    """
    # Get directories
    data_dir = Path("data")
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    
    # Get sets of processed and trained files
    processed_files = get_processed_files()
    trained_files = get_trained_files()
    
    # Find all parquet files in raw directory
    raw_files = set()
    if raw_dir.exists():
        raw_files = {f.name for f in raw_dir.glob("*.parquet")}
    
    # Find all parquet files in processed directory
    processed_dir_files = set()
    if processed_dir.exists():
        processed_dir_files = {f.name for f in processed_dir.glob("*.parquet")}
    
    # Find new files (in raw but not in processed)
    new_files = raw_files - processed_dir_files
    
    # Convert to full paths
    new_file_paths = [str(raw_dir / f) for f in new_files]
    
    return new_file_paths

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