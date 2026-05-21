#!/usr/bin/env python3
"""
Download OpenVINO human pose estimation model for posture detection.

Usage:
    python download_model.py

This will download the human-pose-estimation-0002 model from Open Model Zoo.
"""

import os
import urllib.request
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Model URLs (OpenVINO 2021.4)
MODEL_NAME = "human-pose-estimation-0002"
BASE_URL = "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2021.4/models_bin/3"

WEIGHTS_DIR = Path(__file__).parent.parent / "weights"

MODELS = {
    "human-pose-estimation-0002.xml": f"{BASE_URL}/{MODEL_NAME}/FP32/{MODEL_NAME}.xml",
    "human-pose-estimation-0002.bin": f"{BASE_URL}/{MODEL_NAME}/FP32/{MODEL_NAME}.bin",
}


def download_file(url: str, dest: Path):
    """Download file with progress bar"""
    print(f"Downloading: {url}")
    print(f"Destination: {dest}")

    try:
        urllib.request.urlretrieve(url, dest)
        print(f"[OK] Downloaded: {dest.name}")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to download {dest.name}: {e}")
        return False


def main():
    print("=" * 60)
    print("OpenVINO Human Pose Estimation Model Downloader")
    print("=" * 60)

    # Create weights directory
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nWeights directory: {WEIGHTS_DIR}")

    # Download models
    success = True
    for filename, url in MODELS.items():
        dest = WEIGHTS_DIR / filename

        if dest.exists():
            print(f"[OK] Already exists: {filename}")
            continue

        if not download_file(url, dest):
            success = False

    print("\n" + "=" * 60)
    if success:
        print("All models downloaded successfully!")
        print(f"\nModel files location: {WEIGHTS_DIR}")
    else:
        print("Some models failed to download.")
        print("\nAlternative: Download manually from:")
        print(f"  https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/intel/{MODEL_NAME}")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
