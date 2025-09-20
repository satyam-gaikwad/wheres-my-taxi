#!/usr/bin/env python3
import sys
import argparse
import time
import pandas as pd
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
from monitoring.metrics import MetricsCollector
from monitoring.alerts import AlertManager
from monitoring.reports import ReportGenerator
from monitoring.logger import setup_monitoring_logger

def main():
    """Main function to run the pipeline."""
    print("\n=== Taxi Data Processing Pipeline ===")
    
    # Initialize monitoring
    metrics_collector = MetricsCollector()
    alert_manager = AlertManager()
    report_generator = ReportGenerator()
    logger = setup_monitoring_logger()
    
    # Start pipeline monitoring
    metrics_collector.start_pipeline("wheres_my_taxi_pipeline")
    
    try:
        parser = argparse.ArgumentParser(description='Run the taxi data processing pipeline')
        parser.add_argument('--retrain', action='store_true', help='Force retraining on all existing data')
        args = parser.parse_args()

        original_data = None  # Will store for data quality metrics
        
        if args.retrain:
            print("\nMode: Retraining")
            logger.info("Starting pipeline in retrain mode")
            
            # Use all data files for retraining
            all_files = get_all_data_files()
            if not all_files:
                error_msg = "No data files found for retraining."
                print(f"Error: {error_msg}")
                metrics_collector.add_pipeline_error(error_msg)
                alert_manager.send_pipeline_failure_alert(error_msg)
                print("\n=== Pipeline Status ===")
                print("Pipeline completed with errors.")
                return
            print(f"Found {len(all_files)} data files for retraining.")
            print("Clearing trained files list...")
            save_trained_files(set())  # Clear trained files
        else:
            print("\nMode: Normal Processing")
            logger.info("Starting pipeline in normal mode")
            
            # Only process new files
            all_files = check_new_data()
            if not all_files:
                print("No data files found in the data directory.")
                metrics_collector.complete_pipeline(0)
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
                metrics_collector.complete_pipeline(0)
                print("\n=== Pipeline Status ===")
                print("Pipeline completed - no new files to process.")
                return
                
            print(f"Found {len(all_files)} total files.")
            print(f"Found {len(trained_files)} trained files.")
            print(f"Processing {len(new_files)} new files...")
            all_files = new_files

        # Load original data for quality metrics (sample from first file)
        if all_files:
            try:
                original_data = pd.read_parquet(all_files[0])
                logger.info(f"Loaded sample data from {all_files[0]} for quality metrics")
            except Exception as e:
                warning_msg = f"Could not load sample data for quality metrics: {str(e)}"
                metrics_collector.add_pipeline_warning(warning_msg)
                logger.warning(warning_msg)

        print("\nStarting model training...")
        logger.info("Starting model training phase")
        
        # Train model on all_files
        model, X, y = train_sgd_regressor(all_files)

        # If no files were processed, exit
        if model is None:
            error_msg = "No files were processed during training."
            print(f"Error: {error_msg}")
            metrics_collector.add_pipeline_error(error_msg)
            alert_manager.send_pipeline_failure_alert(error_msg, metrics_collector.get_all_metrics())
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
        
        logger.info(f"Model training completed - MSE: {mse:.2f}, R2: {r2:.2f}")

        # Collect model metrics
        metrics_collector.collect_model_metrics(model, X, y, "SGDRegressor")
        
        # Collect data quality metrics if original data is available
        if original_data is not None:
            # Create a sample processed dataframe for comparison
            processed_sample = pd.DataFrame(X, columns=['PULocationID', 'DOLocationID', 'trip_distance', 'day_number', 'PU_hour'])
            metrics_collector.collect_data_quality_metrics(original_data, processed_sample)
        
        # Complete pipeline metrics
        metrics_collector.complete_pipeline(len(all_files))
        
        # Get all metrics
        all_metrics = metrics_collector.get_all_metrics()
        
        # Check for performance alerts
        if 'model' in all_metrics:
            alert_manager.send_model_performance_alert(all_metrics['model'])
        
        if 'data_quality' in all_metrics:
            alert_manager.send_data_quality_alert(all_metrics['data_quality'])
        
        # Send success status update
        alert_manager.send_workflow_status_update("success", all_metrics.get('pipeline', {}))
        
        # Generate and save monitoring report
        report = report_generator.generate_report(all_metrics)
        report_path = report_generator.save_report(report)
        
        # Save metrics to CSV for historical tracking
        report_generator.save_metrics_csv(all_metrics)
        
        # Generate dashboard data
        metrics_history = report_generator.load_metrics_history()
        dashboard_data = report_generator.generate_dashboard_data(metrics_history)
        
        # Save dashboard files
        report_generator.save_dashboard_data(dashboard_data)
        dashboard_path = report_generator.save_html_dashboard(dashboard_data)
        
        logger.info(f"Monitoring report saved to: {report_path}")
        logger.info(f"Dashboard saved to: {dashboard_path}")

        print("\n=== Pipeline Status ===")
        print("Model training completed successfully.")
        print("Trained files have been saved.")
        print(f"Monitoring report saved to: {report_path}")
        print(f"Dashboard available at: {dashboard_path}")
        
    except Exception as e:
        error_msg = f"Pipeline failed with exception: {str(e)}"
        print(f"Error: {error_msg}")
        
        # Add error to metrics and send alert
        metrics_collector.add_pipeline_error(error_msg)
        alert_manager.send_pipeline_failure_alert(error_msg, metrics_collector.get_all_metrics())
        alert_manager.send_workflow_status_update("failure", metrics_collector.get_all_metrics().get('pipeline', {}))
        
        logger.error(error_msg)
        
        print("\n=== Pipeline Status ===")
        print("Pipeline completed with errors.")
        
        # Still try to save report for debugging
        try:
            all_metrics = metrics_collector.get_all_metrics()
            report = report_generator.generate_report(all_metrics)
            report_path = report_generator.save_report(report)
            print(f"Error report saved to: {report_path}")
        except Exception as report_error:
            print(f"Could not save error report: {report_error}")
        
        raise

if __name__ == "__main__":
    main() 