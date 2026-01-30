#!/bin/bash

# Dataset Setup Automation Script
# This script will download, preprocess, and generate all benchmark datasets

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║              BENCHMARK DATASET SETUP AUTOMATION                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "⚠ uv is not installed."
    echo "Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "Or visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv-benchmark" ]; then
    echo "→ Creating virtual environment with uv..."
    uv venv --python 3.12 .venv-benchmark
fi

# Activate virtual environment
echo "→ Activating virtual environment..."
source .venv-benchmark/bin/activate

# Install dependencies only (not the package itself)
echo "→ Installing dependencies with uv..."
uv pip install pandas numpy scikit-learn ucimlrepo openpyxl kaggle beautifulsoup4 requests

# Run the main setup script
echo ""
echo "→ Running dataset setup..."
echo ""
python scripts/setup_datasets.py

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                      SETUP COMPLETE                               ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "✓ All datasets are ready in: dataset_combined/"
echo ""
