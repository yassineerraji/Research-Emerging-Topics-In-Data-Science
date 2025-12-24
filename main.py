"""
Climate Scenario Pipeline - Main Execution Script

This script orchestrates the complete climate scenario analysis pipeline:
1. Data loading and preprocessing
2. Scenario extraction and analysis
3. Projection generation
4. Visualization and reporting

Run this script to reproduce all results.
"""

import os
import sys
from pathlib import Path

# Import pipeline modules
from src import config, io, processing, scenarios, visualization, utils


def main():
    """
    Main function to run the complete climate scenario analysis pipeline.
    """
    print("="*70)
    print("Climate Scenario Analysis Pipeline")
    print("="*70)
    
    # Initialize configuration
    cfg = config.get_config()
    
    try:
        # Step 1: Data Loading
        print("\n" + "="*70)
        print("STEP 1: Data Loading")
        print("="*70)
        
        utils.log_pipeline_step("Data Loading", "START")
        
        # Check if raw data exists
        raw_files = list(config.RAW_DATA_DIR.glob('*.csv'))
        if not raw_files:
            print("\n⚠️  No data files found in data/raw/")
            print("Please add your climate data CSV files to the data/raw/ directory.")
            print("\nExample data structure expected:")
            print("  - date/time column")
            print("  - scenario column (e.g., RCP2.6, RCP4.5, RCP8.5)")
            print("  - value columns (e.g., temperature, precipitation)")
            print("  - optional: region/location column")
            return
        
        # Load the first available data file
        data_file = raw_files[0]
        print(f"\nLoading data from: {data_file.name}")
        data = io.load_raw_data(data_file.name)
        
        utils.log_pipeline_step("Data Loading", "COMPLETE", f"Loaded {len(data)} records")
        
        # Step 2: Data Quality Check
        print("\n" + "="*70)
        print("STEP 2: Data Quality Assessment")
        print("="*70)
        
        quality_report = utils.check_data_quality(data)
        
        # Step 3: Data Processing
        print("\n" + "="*70)
        print("STEP 3: Data Processing and Harmonization")
        print("="*70)
        
        utils.log_pipeline_step("Data Processing", "START")
        
        # Clean missing values
        data_clean = processing.clean_missing_values(
            data,
            strategy=cfg['processing']['missing_value_strategy']
        )
        
        # Save interim data
        io.save_interim_data(data_clean, 'cleaned_data.csv')
        
        utils.log_pipeline_step("Data Processing", "COMPLETE")
        
        # Step 4: Scenario Analysis
        print("\n" + "="*70)
        print("STEP 4: Scenario Extraction and Analysis")
        print("="*70)
        
        utils.log_pipeline_step("Scenario Analysis", "START")
        
        # Check if data has scenario column
        scenario_cols = [col for col in data_clean.columns 
                        if 'scenario' in col.lower() or 'rcp' in col.lower()]
        
        if scenario_cols:
            scenario_col = scenario_cols[0]
            value_cols = data_clean.select_dtypes(include=['float64', 'int64']).columns.tolist()
            datetime_cols = [col for col in data_clean.columns 
                           if 'date' in col.lower() or 'time' in col.lower() or 'year' in col.lower()]
            
            if datetime_cols and value_cols:
                datetime_col = datetime_cols[0]
                value_col = value_cols[0]
                
                # Run scenario comparison
                available_scenarios = data_clean[scenario_col].unique().tolist()
                print(f"\nFound scenarios: {available_scenarios}")
                
                scenario_summary = scenarios.run_scenario_analysis(
                    data_clean,
                    scenarios=available_scenarios,
                    scenario_col=scenario_col,
                    value_col=value_col,
                    datetime_col=datetime_col
                )
                
                # Save scenario summary
                io.save_table(scenario_summary, 'scenario_summary', format='csv')
                
                utils.log_pipeline_step("Scenario Analysis", "COMPLETE")
            else:
                print("⚠️  Could not identify datetime or value columns for scenario analysis")
        else:
            print("⚠️  No scenario column detected in data")
        
        # Step 5: Visualization
        print("\n" + "="*70)
        print("STEP 5: Generating Visualizations")
        print("="*70)
        
        utils.log_pipeline_step("Visualization", "START")
        
        # Generate visualizations if we have the necessary columns
        if scenario_cols and datetime_cols and value_cols:
            # Time series comparison
            viz_path = config.FIGURES_DIR / 'scenario_comparison.png'
            visualization.plot_scenario_comparison(
                data_clean,
                datetime_col=datetime_col,
                value_col=value_col,
                scenario_col=scenario_col,
                scenarios=available_scenarios,
                title=f"Climate Scenario Comparison: {value_col}",
                save_path=str(viz_path)
            )
            
            # Distribution comparison
            dist_path = config.FIGURES_DIR / 'distribution_comparison.png'
            visualization.plot_distribution_comparison(
                data_clean,
                value_col=value_col,
                group_col=scenario_col,
                title=f"Distribution Across Scenarios: {value_col}",
                save_path=str(dist_path)
            )
            
            # Create dashboard
            dashboard_path = config.FIGURES_DIR / 'dashboard.png'
            visualization.create_dashboard(
                data_clean,
                datetime_col=datetime_col,
                value_cols=value_cols[:4],  # Limit to first 4 variables
                scenario_col=scenario_col,
                save_path=str(dashboard_path)
            )
            
            utils.log_pipeline_step("Visualization", "COMPLETE")
        else:
            print("⚠️  Skipping visualizations - missing required columns")
        
        # Step 6: Export Results Summary
        print("\n" + "="*70)
        print("STEP 6: Exporting Results")
        print("="*70)
        
        results = {
            'data_shape': data_clean.shape,
            'scenarios_analyzed': available_scenarios if scenario_cols else [],
            'quality_report': quality_report,
            'output_directory': str(config.OUTPUT_DIR)
        }
        
        summary_path = config.OUTPUT_DIR / 'pipeline_summary.json'
        utils.export_results_summary(results, str(summary_path), format='json')
        
        # Final Summary
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETE!")
        print("="*70)
        print(f"\n📁 Output Location: {config.OUTPUT_DIR}")
        print("\n📊 Generated Files:")
        print(f"   Data:")
        print(f"     - {config.INTERIM_DATA_DIR}/cleaned_data.csv")
        if scenario_cols:
            print(f"     - {config.TABLES_DIR}/scenario_summary.csv")
        print(f"\n   Figures:")
        for fig_file in config.FIGURES_DIR.glob('*.png'):
            print(f"     - {fig_file.name}")
        print(f"\n   Summary:")
        print(f"     - pipeline_summary.json")
        
        print("\n" + "="*70)
        
    except FileNotFoundError as e:
        utils.log_pipeline_step("Pipeline", "ERROR", str(e))
        print(f"\n❌ ERROR: {e}")
        print("Please ensure your data files are in the correct location.")
    except Exception as e:
        utils.log_pipeline_step("Pipeline", "ERROR", str(e))
        print(f"\n❌ ERROR: An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
