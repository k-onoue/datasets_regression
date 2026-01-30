"""
Script to download and preprocess Taxi dataset from Kaggle.
Requires Kaggle API to be set up with credentials in ~/.kaggle/kaggle.json
"""

import os
import zipfile
import pandas as pd
import numpy as np
from pathlib import Path


def download_taxi_dataset(output_dir: str = "source_data_xu_2024"):
    """
    Download Taxi dataset from Kaggle using the Kaggle API.
    
    Args:
        output_dir: Directory to save the downloaded dataset
    """
    try:
        import kaggle
    except ImportError:
        raise ImportError(
            "Kaggle library not installed. Please run: pip install kaggle\n"
            "Also ensure kaggle.json is placed in ~/.kaggle/"
        )
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("DOWNLOADING TAXI DATASET FROM KAGGLE")
    print("="*60)
    print("Dataset: New York City Taxi Fare Prediction")
    print(f"Output directory: {output_path.absolute()}\n")
    
    try:
        # Authenticate
        kaggle.api.authenticate()
        
        # Download the competition dataset
        print("Downloading dataset (this may take a while)...")
        kaggle.api.competition_download_files(
            'new-york-city-taxi-fare-prediction',
            path=str(output_path),
            quiet=False
        )
        
        # Extract the zip file
        zip_path = output_path / 'new-york-city-taxi-fare-prediction.zip'
        if zip_path.exists():
            print("\nExtracting files...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_path)
            
            # Remove the zip file to save space
            os.remove(zip_path)
            print("✓ Extraction complete")
        
        # Check if train.csv was downloaded (the main file we need)
        train_csv = output_path / 'train.csv'
        if train_csv.exists():
            # Rename to taxi.csv for consistency with the notebook
            taxi_csv = output_path / 'taxi.csv'
            if not taxi_csv.exists():
                os.rename(train_csv, taxi_csv)
                print(f"✓ Renamed train.csv to taxi.csv")
        
        print("\n✓ Download complete!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error downloading Taxi dataset: {e}")
        print("\nPlease ensure:")
        print("1. Kaggle API is installed: pip install kaggle")
        print("2. kaggle.json is placed in ~/.kaggle/")
        print("3. File permissions: chmod 600 ~/.kaggle/kaggle.json")
        print("4. ⚠ IMPORTANT: You have accepted the competition rules at:")
        print("   https://www.kaggle.com/c/new-york-city-taxi-fare-prediction/rules")
        print("   (Visit the URL above and click 'I Understand and Accept')")
        return False


def preprocess_taxi_dataset(
    input_file: str = "source_data_xu_2024/taxi.csv",
    output_file: str = "source_data_xu_2024/taxi_subset.csv",
    nrows: int = 200000
):
    """
    Preprocess the Taxi dataset by:
    1. Loading a subset of rows
    2. Converting datetime columns
    3. Creating trip_duration feature
    4. Encoding categorical variables
    5. Removing unnecessary columns
    
    Args:
        input_file: Path to the raw taxi.csv file
        output_file: Path to save the preprocessed taxi_subset.csv
        nrows: Number of rows to load from the dataset
    """
    print("\n" + "="*60)
    print("PREPROCESSING TAXI DATASET")
    print("="*60)
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"✗ Input file not found: {input_file}")
        return False
    
    try:
        print(f"Loading first {nrows:,} rows from {input_file}...")
        df = pd.read_csv(input_file, nrows=nrows)
        
        print(f"✓ Loaded {len(df):,} rows")
        print(f"  Columns: {', '.join(df.columns)}")
        
        # Check if this is the NYC Taxi dataset format
        if 'tpep_pickup_datetime' in df.columns:
            print("\nDetected NYC Taxi Trip format (2016 onwards)")
            
            # Convert store_and_fwd_flag
            if 'store_and_fwd_flag' in df.columns:
                df['store_and_fwd_flag'] = df['store_and_fwd_flag'].map({'N': 0, 'Y': 1})
                print("✓ Encoded store_and_fwd_flag")
            
            # Convert datetime columns
            df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
            df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
            print("✓ Converted datetime columns")
            
            # Create trip_duration feature
            df['trip_duration'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds()
            print("✓ Created trip_duration feature")
            
            # Drop datetime columns
            df = df.drop(columns=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
            
        elif 'pickup_datetime' in df.columns:
            print("\nDetected Kaggle Taxi Fare format")
            
            # Convert datetime column
            df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
            
            # Extract temporal features
            df['pickup_year'] = df['pickup_datetime'].dt.year
            df['pickup_month'] = df['pickup_datetime'].dt.month
            df['pickup_day'] = df['pickup_datetime'].dt.day
            df['pickup_hour'] = df['pickup_datetime'].dt.hour
            df['pickup_weekday'] = df['pickup_datetime'].dt.weekday
            print("✓ Extracted temporal features")
            
            # Calculate distance (haversine formula)
            def haversine_distance(lat1, lon1, lat2, lon2):
                R = 6371  # Earth radius in km
                dlat = np.radians(lat2 - lat1)
                dlon = np.radians(lon2 - lon1)
                a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
                c = 2 * np.arcsin(np.sqrt(a))
                return R * c
            
            df['distance_km'] = haversine_distance(
                df['pickup_latitude'], df['pickup_longitude'],
                df['dropoff_latitude'], df['dropoff_longitude']
            )
            print("✓ Calculated trip distance")
            
            # Drop datetime column
            df = df.drop(columns=['pickup_datetime'])
        
        # Check data types
        print(f"\n✓ Data types:")
        print(df.dtypes)
        
        # Check for missing values
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            print(f"\n⚠ Missing values detected:")
            print(null_counts[null_counts > 0])
            print("  Dropping rows with missing values...")
            df = df.dropna()
            print(f"  Remaining rows: {len(df):,}")
        else:
            print("\n✓ No missing values")
        
        # Save preprocessed dataset
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_file, index=False)
        
        print(f"\n✓ Saved preprocessed dataset to: {output_file}")
        print(f"  Final shape: {df.shape}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error preprocessing Taxi dataset: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    Main function to download and preprocess Taxi dataset.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download and preprocess NYC Taxi dataset from Kaggle"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="source_data_xu_2024",
        help="Output directory for downloaded and processed files"
    )
    parser.add_argument(
        "-n", "--nrows",
        type=int,
        default=200000,
        help="Number of rows to load from the dataset (default: 200000)"
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip download step (use existing taxi.csv)"
    )
    parser.add_argument(
        "--skip-preprocess",
        action="store_true",
        help="Skip preprocessing step"
    )
    
    args = parser.parse_args()
    
    # Download
    if not args.skip_download:
        success = download_taxi_dataset(args.output_dir)
        if not success:
            print("\n⚠ Download failed, but continuing...")
    
    # Preprocess
    if not args.skip_preprocess:
        input_file = os.path.join(args.output_dir, "taxi.csv")
        output_file = os.path.join(args.output_dir, "taxi_subset.csv")
        
        success = preprocess_taxi_dataset(
            input_file=input_file,
            output_file=output_file,
            nrows=args.nrows
        )
        
        if success:
            print("\n" + "="*60)
            print("✓ TAXI DATASET READY")
            print("="*60)
        else:
            print("\n⚠ Preprocessing failed")


if __name__ == "__main__":
    main()
