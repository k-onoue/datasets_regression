# Benchmark Datasets

This repository contains scripts to automatically download, preprocess, and generate benchmark datasets for regression tasks.

## Quick Start

**Single command to set up all datasets:**

```bash
./run.sh
```

Or directly with Python:

```bash
python scripts/setup_datasets.py
```

This will:
1. Download KEEL datasets (diabetes, machineCPU, ele-1)
2. Download and preprocess NYC Taxi dataset from Kaggle
3. Generate Tang 2017 datasets → `dataset_combined/`
4. Generate Xu 2024 datasets → `dataset_combined/`

## Prerequisites

### 1. Python Environment Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv --python 3.12 .venv-benchmark
source .venv-benchmark/bin/activate
uv pip install pandas numpy scikit-learn ucimlrepo openpyxl kaggle beautifulsoup4 requests
```

**Note:** The `./run.sh` script will automatically handle environment setup if uv is installed.

Dependencies are managed in [pyproject.toml](pyproject.toml).

### 2. Kaggle API Setup (Required for Taxi dataset)

```bash
# Kaggle is included in project dependencies

# Download kaggle.json from your Kaggle account:
# Account → Settings → API → Create New Token

# Place it in the correct location
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Accept competition rules at:
# https://www.kaggle.com/c/new-york-city-taxi-fare-prediction
```

## Output Structure

All datasets are saved to `dataset_combined/` with the following structure:

```
dataset_combined/
├── Bike/
│   ├── split_0/
│   │   ├── train_features.csv
│   │   ├── train_target.csv
│   │   ├── test_features.csv
│   │   └── test_target.csv
│   ├── split_1/
│   └── ...
├── Bike_Outliers/
├── Boston/
├── Boston_Outliers/
├── Concrete/
├── Concrete_Outliers/
├── Diabetes/
├── Diabetes_Outliers/
├── ELE/
├── ELE_Outliers/
├── Energy/
├── Energy_Outliers/
├── Elevators/
├── Elevators_Outliers/
├── Kin8nm/
├── Kin8nm_Outliers/
├── Machine_CPU/
├── Machine_CPU_Outliers/
├── MPG/
├── MPG_Outliers/
├── Neal/
├── Neal_XOutlier/
├── Neal_YOutlier/
├── Protein/
├── Protein_Outliers/
├── Taxi/
├── Taxi_Outliers/
├── Yacht/
└── Yacht_Outliers/
```

Each dataset contains 10 splits (split_0 to split_9) with train/test features and targets.

## Dataset Sources

### Tang 2017 Datasets

**Reference:** Tang, Qingtao, et al. "Student-t process regression with student-t likelihood." International Joint Conference on Artificial Intelligence 2017. Association for the Advancement of Artificial Intelligence (AAAI), 2017.

**Datasets:**
- Bike (UCI ML Repository)
- Concrete (UCI ML Repository)
- Diabetes (KEEL)
- ELE (KEEL)
- Machine_CPU (KEEL)
- MPG (UCI ML Repository)
- Neal (Synthetic dataset)

### Xu 2024 Datasets

**Reference:** Xu, Jian, and Delu Zeng. "Sparse variational student-t processes." Proceedings of the AAAI Conference on Artificial Intelligence. Vol. 38. No. 14. 2024.

**Datasets:**
- Boston (OpenML)
- Concrete (UCI ML Repository)
- Energy (UCI ML Repository)
- Elevators (OpenML)
- Kin8nm (OpenML)
- Protein (UCI ML Repository)
- Taxi (Kaggle - NYC Taxi Fare Prediction)
- Yacht (UCI ML Repository)

## Manual Setup (Alternative)

If you prefer to run individual steps:

### Step 1: Download KEEL Datasets

```bash
python scripts/download_keel_datasets.py -o source_data_tang_2017 -d diabetes machineCPU ele-1
```

### Step 2: Download and Preprocess Taxi Dataset

```bash
python scripts/download_and_process_taxi.py -o source_data_xu_2024 -n 200000
```

### Step 3: Generate Tang 2017 Datasets

```bash
python scripts/create_dataset_tang_2017.py
```

### Step 4: Generate Xu 2024 Datasets

```bash
python scripts/create_dataset_xu_2024.py
```

## Individual Script Usage

### download_keel_datasets.py

Download datasets from KEEL repository:

```bash
# List all available datasets
python scripts/download_keel_datasets.py --list

# Download specific datasets
python scripts/download_keel_datasets.py -d diabetes machineCPU ele-1 -o keel_datasets

# Download with 5-fold partitions
python scripts/download_keel_datasets.py -d diabetes -p
```

### download_and_process_taxi.py

Download and preprocess Taxi dataset:

```bash
# Full process (download + preprocess)
python scripts/download_and_process_taxi.py -o source_data_xu_2024 -n 200000

# Skip download (if you already have taxi.csv)
python scripts/download_and_process_taxi.py --skip-download

# Skip preprocessing
python scripts/download_and_process_taxi.py --skip-preprocess
```

## Troubleshooting

### Kaggle API Issues

```bash
# Check if Kaggle is properly configured
python -c "import kaggle; kaggle.api.authenticate(); print('✓ Kaggle OK')"
```

If you see an error:
1. Ensure `~/.kaggle/kaggle.json` exists
2. Check file permissions: `chmod 600 ~/.kaggle/kaggle.json`
3. Accept competition rules at the Kaggle website

### Missing Python Packages

All required packages are specified in [pyproject.toml](pyproject.toml). If you need to reinstall:

```bash
uv pip install pandas numpy scikit-learn ucimlrepo openpyxl kaggle beautifulsoup4 requests
```

### KEEL Download Fails

The KEEL repository might be temporarily unavailable. Try again later or manually download from:
https://sci2s.ugr.es/keel/category.php?cat=reg

Place `.dat` files in `source_data_tang_2017/`

## Notes

- All datasets are standardized (StandardScaler applied within each train/test split)
- Outlier versions contain 5% of samples with target values shifted by +3σ
- Neal dataset includes synthetic data with optional input (X) or target (Y) outliers
- The Taxi dataset uses a 200,000-row subset by default (configurable)