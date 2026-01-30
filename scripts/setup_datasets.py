#!/usr/bin/env python3
"""
Master script to set up all datasets for the project.
Automatically downloads, preprocesses, and generates all datasets into dataset_combined/.

Requirements:
- Python packages: pandas, numpy, scikit-learn, ucimlrepo, openpyxl, kaggle, beautifulsoup4, requests
- Kaggle API credentials in ~/.kaggle/kaggle.json
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def check_requirements():
    """Check if required packages are installed."""
    print_header("CHECKING REQUIREMENTS")
    
    required_packages = [
        'pandas',
        'numpy',
        'sklearn',
        'ucimlrepo',
        'openpyxl',
        'kaggle',
        'bs4',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n⚠ Missing packages detected!")
        print("Install them with:")
        # Map bs4 to beautifulsoup4 for pip install
        install_names = ['beautifulsoup4' if p == 'bs4' else 'scikit-learn' if p == 'sklearn' else p for p in missing_packages]
        print(f"  pip install {' '.join(install_names)}")
        return False
    
    print("\n✓ All required packages are installed")
    return True


def check_kaggle_setup():
    """Check if Kaggle API is properly configured."""
    print_header("CHECKING KAGGLE API SETUP")
    
    try:
        import kaggle
        kaggle.api.authenticate()
        print("✓ Kaggle API is properly configured")
        return True
    except Exception as e:
        print(f"✗ Kaggle API setup issue: {e}")
        print("\nPlease ensure:")
        print("1. Install Kaggle: pip install kaggle")
        print("2. Download kaggle.json from your Kaggle account settings")
        print("3. Place it in ~/.kaggle/kaggle.json")
        print("4. Set permissions: chmod 600 ~/.kaggle/kaggle.json")
        print("5. Accept competition rules at:")
        print("   https://www.kaggle.com/c/new-york-city-taxi-fare-prediction")
        return False


def download_keel_datasets():
    """Download required datasets from KEEL repository."""
    print_header("STEP 1/4: DOWNLOADING KEEL DATASETS")
    
    required_datasets = ['diabetes', 'machineCPU', 'ele-1']
    
    try:
        from download_keel_datasets import download_datasets
        
        download_datasets(
            output_dir='source_data_tang_2017',
            datasets=required_datasets,
            download_partitions=False,
            keep_zip=False
        )
        
        print("\n✓ KEEL datasets downloaded successfully")
        return True
        
    except Exception as e:
        print(f"\n✗ Error downloading KEEL datasets: {e}")
        import traceback
        traceback.print_exc()
        return False


def download_and_process_taxi():
    """Download and preprocess Taxi dataset from Kaggle."""
    print_header("STEP 2/4: DOWNLOADING AND PREPROCESSING TAXI DATASET")
    
    try:
        from download_and_process_taxi import download_taxi_dataset, preprocess_taxi_dataset
        
        # Download
        success = download_taxi_dataset('source_data_xu_2024')
        if not success:
            print("⚠ Taxi download had issues, but continuing...")
        
        # Preprocess
        success = preprocess_taxi_dataset(
            input_file='source_data_xu_2024/taxi.csv',
            output_file='source_data_xu_2024/taxi_subset.csv',
            nrows=200000
        )
        
        if success:
            print("\n✓ Taxi dataset ready")
            return True
        else:
            print("\n⚠ Taxi preprocessing had issues")
            return False
            
    except Exception as e:
        print(f"\n✗ Error with Taxi dataset: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_tang_datasets():
    """Generate datasets from Tang 2017."""
    print_header("STEP 3/4: GENERATING TANG 2017 DATASETS")
    
    try:
        script_dir = Path(__file__).parent
        script_path = script_dir / "create_dataset_tang_2017.py"
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            cwd=script_dir.parent,
            capture_output=False
        )
        
        print("\n✓ Tang 2017 datasets generated successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error generating Tang 2017 datasets: Process exited with code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ Error generating Tang 2017 datasets: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_xu_datasets():
    """Generate datasets from Xu 2024."""
    print_header("STEP 4/4: GENERATING XU 2024 DATASETS")
    
    try:
        script_dir = Path(__file__).parent
        script_path = script_dir / "create_dataset_xu_2024.py"
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            cwd=script_dir.parent,
            capture_output=False
        )
        
        print("\n✓ Xu 2024 datasets generated successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error generating Xu 2024 datasets: Process exited with code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ Error generating Xu 2024 datasets: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_output():
    """Verify that all expected datasets were created."""
    print_header("VERIFICATION")
    
    output_dir = Path('dataset_combined')
    
    if not output_dir.exists():
        print("✗ Output directory 'dataset_combined' does not exist")
        return False
    
    expected_datasets = [
        # Tang 2017 datasets
        'Bike', 'Bike_Outliers',
        'Concrete', 'Concrete_Outliers',
        'Diabetes', 'Diabetes_Outliers',
        'ELE', 'ELE_Outliers',
        'Machine_CPU', 'Machine_CPU_Outliers',
        'MPG', 'MPG_Outliers',
        'Neal', 'Neal_XOutlier', 'Neal_YOutlier',
        # Xu 2024 datasets
        'Boston', 'Boston_Outliers',
        'Energy', 'Energy_Outliers',
        'Elevators', 'Elevators_Outliers',
        'Kin8nm', 'Kin8nm_Outliers',
        'Protein', 'Protein_Outliers',
        'Yacht', 'Yacht_Outliers',
        'Taxi', 'Taxi_Outliers',
    ]
    
    found_datasets = []
    missing_datasets = []
    
    for dataset in expected_datasets:
        dataset_path = output_dir / dataset
        if dataset_path.exists() and dataset_path.is_dir():
            # Check if it has splits
            splits = list(dataset_path.glob('split_*'))
            if splits:
                found_datasets.append(f"{dataset} ({len(splits)} splits)")
            else:
                missing_datasets.append(f"{dataset} (no splits)")
        else:
            missing_datasets.append(dataset)
    
    print(f"Found {len(found_datasets)} datasets:")
    for dataset in sorted(found_datasets):
        print(f"  ✓ {dataset}")
    
    if missing_datasets:
        print(f"\n⚠ Missing {len(missing_datasets)} datasets:")
        for dataset in sorted(missing_datasets):
            print(f"  ✗ {dataset}")
        return False
    
    print(f"\n✓ All {len(expected_datasets)} datasets successfully created!")
    return True


def main():
    """Main orchestration function."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                   DATASET SETUP AUTOMATION                        ║
║                                                                   ║
║  This script will:                                                ║
║  1. Download KEEL datasets (diabetes, machineCPU, ele-1)          ║
║  2. Download and preprocess NYC Taxi dataset from Kaggle          ║
║  3. Generate Tang 2017 datasets                                   ║
║  4. Generate Xu 2024 datasets                                     ║
║                                                                   ║
║  Output: dataset_combined/                                        ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Check requirements
    if not check_requirements():
        print("\n⚠ Please install missing packages before continuing.")
        sys.exit(1)
    
    if not check_kaggle_setup():
        print("\n⚠ Please set up Kaggle API before continuing.")
        print("   (Or manually download taxi.csv and place it in source_data_xu_2024/)")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Execute steps
    success = True
    
    # Step 1: Download KEEL datasets
    if not download_keel_datasets():
        print("\n⚠ KEEL download failed. Please check your internet connection.")
        success = False
    
    # Step 2: Download and process Taxi
    if not download_and_process_taxi():
        print("\n⚠ Taxi dataset failed. Continuing with other datasets...")
        # Don't set success to False - we can continue without Taxi
    
    # Step 3: Generate Tang 2017 datasets
    if not generate_tang_datasets():
        print("\n✗ Tang 2017 dataset generation failed")
        success = False
    
    # Step 4: Generate Xu 2024 datasets
    if not generate_xu_datasets():
        print("\n✗ Xu 2024 dataset generation failed")
        success = False
    
    # Verify output
    if success:
        verify_output()
    
    # Final summary
    print_header("SETUP COMPLETE")
    if success:
        print("✓ All datasets have been successfully generated!")
        print("✓ Output location: dataset_combined/")
        print("\nDataset structure:")
        print("  dataset_combined/")
        print("    ├── <Dataset_Name>/")
        print("    │   ├── split_0/")
        print("    │   │   ├── train_features.csv")
        print("    │   │   ├── train_target.csv")
        print("    │   │   ├── test_features.csv")
        print("    │   │   └── test_target.csv")
        print("    │   ├── split_1/")
        print("    │   └── ...")
    else:
        print("⚠ Setup completed with some errors. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
