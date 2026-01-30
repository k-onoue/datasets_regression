"""
Script to automatically download .dat files from KEEL regression dataset repository.
URL: https://sci2s.ugr.es/keel/category.php?cat=reg
"""

import requests
from bs4 import BeautifulSoup
import os
import zipfile
from pathlib import Path
import argparse
from typing import List, Dict


def fetch_dataset_list(url: str = "https://sci2s.ugr.es/keel/category.php?cat=reg") -> List[Dict[str, str]]:
    """
    Fetch the list of available datasets from KEEL repository.
    
    Returns:
        List of dictionaries containing dataset information (name, attributes, instances, etc.)
    """
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all table rows with dataset information
    datasets = []
    table = soup.find('table')
    
    if not table:
        print("Could not find dataset table on page")
        return datasets
    
    rows = table.find_all('tr')[1:]  # Skip header row
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 6:  # Ensure we have enough columns
            dataset_name = cols[0].get_text(strip=True)
            
            # Skip empty rows or special rows
            if not dataset_name or dataset_name == "All data sets" or "Visits since" in dataset_name:
                continue
            
            # Extract download links
            links = cols[-3:]  # Last 3 columns contain download links
            zip_links = []
            for link_col in links:
                a_tag = link_col.find('a')
                if a_tag and a_tag.get('href'):
                    zip_links.append(a_tag.get('href'))
            
            datasets.append({
                'name': dataset_name,
                'attributes': cols[1].get_text(strip=True),
                'instances': cols[2].get_text(strip=True),
                'missing_values': cols[3].get_text(strip=True),
                'zip_link': zip_links[0] if len(zip_links) > 0 else None,
                'partitions_link': zip_links[1] if len(zip_links) > 1 else None,
                'header_link': zip_links[2] if len(zip_links) > 2 else None,
            })
    
    return datasets


def download_file(url: str, output_dir: Path) -> str:
    """
    Download a file from the given URL to the output directory.
    
    Args:
        url: URL to download from
        output_dir: Directory to save the file
        
    Returns:
        Path to the downloaded file
    """
    # Make URL absolute if it's relative
    if not url.startswith('http'):
        base_url = "https://sci2s.ugr.es/keel/"
        url = base_url + url.lstrip('/')
    
    filename = url.split('/')[-1]
    output_path = output_dir / filename
    
    print(f"Downloading {filename}...", end=' ')
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print("✓")
    return str(output_path)


def extract_dat_files(zip_path: str, output_dir: Path, keep_zip: bool = False):
    """
    Extract .dat files from a ZIP archive.
    
    Args:
        zip_path: Path to the ZIP file
        output_dir: Directory to extract files to
        keep_zip: Whether to keep the ZIP file after extraction
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract only .dat files
        dat_files = [f for f in zip_ref.namelist() if f.endswith('.dat')]
        for dat_file in dat_files:
            zip_ref.extract(dat_file, output_dir)
            print(f"  Extracted: {dat_file}")
    
    if not keep_zip:
        os.remove(zip_path)


def download_datasets(
    output_dir: str = "keel_datasets",
    datasets: List[str] = None,
    download_partitions: bool = False,
    keep_zip: bool = False
):
    """
    Download datasets from KEEL repository.
    
    Args:
        output_dir: Directory to save downloaded files
        datasets: List of specific dataset names to download (None = all)
        download_partitions: Whether to download 5-fold partitions
        keep_zip: Whether to keep ZIP files after extraction
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("Fetching dataset list from KEEL repository...")
    all_datasets = fetch_dataset_list()
    print(f"Found {len(all_datasets)} datasets")
    
    # Filter datasets if specific names provided
    if datasets:
        all_datasets = [d for d in all_datasets if d['name'] in datasets]
        print(f"Filtering to {len(all_datasets)} requested datasets")
    
    if not all_datasets:
        print("No datasets to download")
        return
    
    print(f"\nDownloading to: {output_path.absolute()}\n")
    
    for i, dataset in enumerate(all_datasets, 1):
        print(f"[{i}/{len(all_datasets)}] {dataset['name']}")
        
        try:
            # Download main dataset
            if dataset['zip_link']:
                zip_path = download_file(dataset['zip_link'], output_path)
                extract_dat_files(zip_path, output_path, keep_zip)
            
            # Download partitions if requested
            if download_partitions and dataset['partitions_link']:
                print(f"  Downloading partitions...", end=' ')
                partition_zip = download_file(dataset['partitions_link'], output_path)
                extract_dat_files(partition_zip, output_path, keep_zip)
            
            print()
            
        except Exception as e:
            print(f"  Error downloading {dataset['name']}: {e}")
            continue
    
    print(f"\nDownload complete! Files saved to: {output_path.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="Download .dat files from KEEL regression dataset repository"
    )
    parser.add_argument(
        "-o", "--output",
        default="keel_datasets",
        help="Output directory for downloaded files (default: keel_datasets)"
    )
    parser.add_argument(
        "-d", "--datasets",
        nargs="+",
        help="Specific dataset names to download (default: all datasets)"
    )
    parser.add_argument(
        "-p", "--partitions",
        action="store_true",
        help="Also download 5-fold cross-validation partitions"
    )
    parser.add_argument(
        "-k", "--keep-zip",
        action="store_true",
        help="Keep ZIP files after extraction"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available datasets and exit"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("Fetching dataset list from KEEL repository...\n")
        datasets = fetch_dataset_list()
        print(f"{'Name':<20} {'Attributes':<15} {'Instances':<10} {'Missing Values'}")
        print("-" * 70)
        for d in datasets:
            print(f"{d['name']:<20} {d['attributes']:<15} {d['instances']:<10} {d['missing_values']}")
        print(f"\nTotal: {len(datasets)} datasets")
        return
    
    download_datasets(
        output_dir=args.output,
        datasets=args.datasets,
        download_partitions=args.partitions,
        keep_zip=args.keep_zip
    )


if __name__ == "__main__":
    main()
