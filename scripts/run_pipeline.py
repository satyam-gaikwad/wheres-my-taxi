#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.pipeline import (
    preprocessing,
    train_sgd_regressor,
    get_trained_files,
    save_trained_files
)
from utils.check_new_data_test import check_new_data, get_all_data_files

def main():
    """Main function to run the pipeline."""
    print("\n=== Taxi Data Processing Pipeline ===")
    
    parser = argparse.ArgumentParser(description='Run the taxi data processing pipeline')
    parser.add_argument('--retrain', action='store_true', help='Force retraining on all existing data')
    args = parser.parse_args()

    if args.retrain:
        print("\nMode: Retraining")
        # Use all data files for retraining
        all_files = get_all_data_files()
        if not all_files:
            print("Error: No data files found for retraining.")
            print("\n=== Pipeline Status ===")
            print("Pipeline completed with errors.")
            return
        print(f"Found {len(all_files)} data files for retraining.")
        print("Clearing trained files list...")
        save_trained_files(set())  # Clear trained files
    else:
        print("\nMode: Normal Processing")
        # Only process new files
        all_files = check_new_data()
        if not all_files:
            print("No data files found in the data directory.")
            print("\n=== Pipeline Status ===")
            print("Pipeline completed - no data to process.")
            return
            
        trained_files = get_trained_files()
        new_files = [f for f in all_files if f not in trained_files]
        
        if not new_files:
            print(f"Found {len(all_files)} total files.")
            print(f"Found {len(trained_files)} trained files.")
            print("Status: All files have been processed.")
            print("No new files to process.")
            print("\n=== Pipeline Status ===")
            print("Pipeline completed - no new files to process.")
            return
            
        print(f"Found {len(all_files)} total files.")
        print(f"Found {len(trained_files)} trained files.")
        print(f"Processing {len(new_files)} new files...")
        all_files = new_files

    print("\nStarting model training...")
    # Train model on all_files
    model, X, y = train_sgd_regressor(all_files)

    # If no files were processed, exit
    if model is None:
        print("Error: No files were processed during training.")
        print("\n=== Pipeline Status ===")
        print("Pipeline completed with errors.")
        return

    # Calculate performance metrics
    from sklearn.metrics import mean_squared_error, r2_score
    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    print("\n=== Model Performance ===")
    print(f"Mean Squared Error: {mse:.2f}")
    print(f"R2 Score: {r2:.2f}")

    print("\n=== Pipeline Status ===")
    print("Model training completed successfully.")
    print("Trained files have been saved.")

if __name__ == "__main__":
    main() 