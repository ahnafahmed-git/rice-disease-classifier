"""
setup_folders.py
Run once to create the initial dataset folder structure under backend/dataset/.
After running, place your training images in each folder manually.

Usage:
    python scripts/setup_folders.py
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR  = os.path.join(PROJECT_ROOT, "backend", "dataset")

INITIAL_CLASSES = [
    "bacterial_leaf_blight",
    "brown_spot",
    "healthy",
    "leaf_blast",
    "leaf_scald",
    "narrow_brown_spot",
]

def setup():
    os.makedirs(DATASET_DIR, exist_ok=True)
    print(f"Dataset root: {DATASET_DIR}\n")
    for cls in INITIAL_CLASSES:
        path = os.path.join(DATASET_DIR, cls)
        os.makedirs(path, exist_ok=True)
        print(f"  ✓ {cls}/")
    print(
        "\nDone. Place your training images inside each folder, "
        "then run: python backend/train.py"
    )

if __name__ == "__main__":
    setup()