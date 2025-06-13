import os
import json
from typing import Set
from pathlib import Path

# Define paths for tracking files
PROCESSED_FILES_PATH = Path("data/processed_files.json")
TRAINED_FILES_PATH = Path("data/trained_files.json")

def save_processed_files(files: Set[str]) -> None:
    """
    Save the set of processed files to a JSON file.
    
    Args:
        files: Set of processed file names
    """
    # Create directory if it doesn't exist
    PROCESSED_FILES_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Save files to JSON
    with open(PROCESSED_FILES_PATH, 'w') as f:
        json.dump(list(files), f)

def get_processed_files() -> Set[str]:
    """
    Get the set of processed files from the JSON file.
    
    Returns:
        Set of processed file names
    """
    if not PROCESSED_FILES_PATH.exists():
        return set()
    
    with open(PROCESSED_FILES_PATH, 'r') as f:
        return set(json.load(f))

def save_trained_files(files: Set[str]) -> None:
    """
    Save the set of trained files to a JSON file.
    
    Args:
        files: Set of trained file names
    """
    # Create directory if it doesn't exist
    TRAINED_FILES_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Save files to JSON
    with open(TRAINED_FILES_PATH, 'w') as f:
        json.dump(list(files), f)

def get_trained_files() -> Set[str]:
    """
    Get the set of trained files from the JSON file.
    
    Returns:
        Set of trained file names
    """
    if not TRAINED_FILES_PATH.exists():
        return set()
    
    with open(TRAINED_FILES_PATH, 'r') as f:
        return set(json.load(f))

def clear_file_tracking() -> None:
    """
    Clear all file tracking data.
    """
    if PROCESSED_FILES_PATH.exists():
        PROCESSED_FILES_PATH.unlink()
    if TRAINED_FILES_PATH.exists():
        TRAINED_FILES_PATH.unlink() 