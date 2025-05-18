import os
import kaggle
import shutil
from pathlib import Path

def download_and_setup_dataset():
    # Create necessary directories
    dataset_dir = Path('dataset/birds')
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # Download dataset from Kaggle
    print("Downloading dataset from Kaggle...")
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(
        'umairshahpirzada/birds-20-species-image-classification',
        path='dataset',
        unzip=True
    )
    
    # Expected structure after download:
    # - Training set: dataset/birds/train/{species}/
    # - Validation set: dataset/birds/valid/{species}/
    # - Test set: dataset/birds/test/{species}/
    
    print("Dataset downloaded and extracted successfully!")
    print("\nDataset structure:")
    print(f"- Training images: dataset/birds/train/")
    print(f"- Validation images: dataset/birds/valid/")
    print(f"- Test images: dataset/birds/test/")

if __name__ == '__main__':
    download_and_setup_dataset() 