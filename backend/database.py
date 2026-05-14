"""
database.py
Manages the dataset directory structure and class label registry.

Dataset layout:
    backend/dataset/
        <class_folder>/
            image1.jpg
            image2.jpg
            ...

Labels are persisted in class_labels.json so display names
survive server restarts and can be bundled into the TF.js ZIP.
"""

import os
import json

BACKEND_DIR  = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR  = os.path.join(BACKEND_DIR, "dataset")
LABELS_FILE  = os.path.join(BACKEND_DIR, "class_labels.json")

# ── Seed data ─────────────────────────────────────────────
_DEFAULT_DISPLAY = {
    "bacterial_leaf_blight": "Bacterial Leaf Blight",
    "brown_spot":            "Brown Spot",
    "healthy":               "Healthy",
    "leaf_blast":            "Leaf Blast",
    "leaf_scald":            "Leaf Scald",
    "narrow_brown_spot":     "Narrow Brown Spot",
}

_DEFAULT_DESCRIPTIONS = {
    "bacterial_leaf_blight": "A serious bacterial disease causing water-soaked to yellowish stripes on leaf margins that eventually turn white to light grey. Caused by Xanthomonas oryzae pv. oryzae.",
    "brown_spot":            "A fungal disease causing small, circular to oval brown spots with a grey or whitish centre on leaves. Caused by Cochliobolus miyabeanus.",
    "healthy":               "No disease detected. The leaf appears to be in a healthy condition with no visible lesions or discolouration.",
    "leaf_blast":            "A fungal disease producing characteristic diamond-shaped lesions with grey or white centres and brown borders on leaves. Caused by Magnaporthe oryzae.",
    "leaf_scald":            "A disease causing onion-green to pale yellow-green lesions along leaf margins, often with brown, water-soaked stripes. Caused by Microdochium oryzae.",
    "narrow_brown_spot":     "Characterised by narrow, linear brown lesions running parallel to the leaf veins. Caused by Cercospora janseana.",
}


def ensure_dataset_dir():
    """Creates dataset root and default class folders if they don't exist."""
    os.makedirs(DATASET_DIR, exist_ok=True)
    for cls in _DEFAULT_DISPLAY:
        os.makedirs(os.path.join(DATASET_DIR, cls), exist_ok=True)
    # Seed labels file if missing
    if not os.path.exists(LABELS_FILE):
        save_labels(_DEFAULT_DISPLAY, _DEFAULT_DESCRIPTIONS)


def load_labels():
    """Returns (display_names: dict, descriptions: dict)."""
    if os.path.exists(LABELS_FILE):
        with open(LABELS_FILE) as f:
            data = json.load(f)
        return data.get("display_names", {}), data.get("descriptions", {})
    return dict(_DEFAULT_DISPLAY), dict(_DEFAULT_DESCRIPTIONS)


def save_labels(display_names: dict, descriptions: dict):
    with open(LABELS_FILE, "w") as f:
        json.dump({"display_names": display_names, "descriptions": descriptions}, f, indent=2)


def get_classes() -> list:
    """Returns sorted list of class folder names discovered in dataset/."""
    ensure_dataset_dir()
    return sorted(
        d for d in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, d))
    )


def add_class(folder_name: str, display_name: str, description: str = "") -> tuple:
    """
    Creates a new class folder and registers it in labels JSON.
    Returns (success: bool, message: str).
    """
    target = os.path.join(DATASET_DIR, folder_name)
    if os.path.exists(target):
        return False, "Class folder already exists."
    os.makedirs(target)
    display, descs = load_labels()
    display[folder_name] = display_name
    if description:
        descs[folder_name] = description
    save_labels(display, descs)
    return True, "Class created."


def save_images(folder_name: str, files: list) -> int:
    """
    Saves uploaded FileStorage objects to the class folder.
    Returns number of files saved.
    """
    target = os.path.join(DATASET_DIR, folder_name)
    os.makedirs(target, exist_ok=True)
    count = 0
    for f in files:
        dest = os.path.join(target, f.filename)
        f.save(dest)
        count += 1
    return count


def get_image_counts() -> dict:
    """Returns {class_folder: image_count} for all classes."""
    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    counts = {}
    for cls in get_classes():
        cls_dir = os.path.join(DATASET_DIR, cls)
        counts[cls] = sum(
            1 for f in os.listdir(cls_dir)
            if os.path.splitext(f)[1].lower() in IMAGE_EXTS
        )
    return counts