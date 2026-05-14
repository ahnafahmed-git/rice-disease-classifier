"""
convert_model.py
Converts backend/saved_model/best_model.h5 → TF.js LayersModel format.
Also writes class_labels.json into the output so the download ZIP
contains everything the frontend needs.

Usage:
    python convert_model.py          (standalone)
    from convert_model import convert  (called by app.py after training)
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess

from database import BACKEND_DIR, get_classes, load_labels

MODEL_H5    = os.path.join(BACKEND_DIR, "saved_model", "best_model.h5")
TFJS_OUTPUT = os.path.join(BACKEND_DIR, "tfjs_model")
ZIP_OUTPUT  = os.path.join(BACKEND_DIR, "tfjs_model.zip")


def convert() -> str:
    """
    Converts .h5 → TF.js, writes class_labels.json, zips everything.
    Returns path to the TFJS output directory.
    Raises RuntimeError on failure.
    """
    if not os.path.exists(MODEL_H5):
        raise RuntimeError(f"Model not found at {MODEL_H5}. Run training first.")

    # Clean and recreate output dir
    if os.path.exists(TFJS_OUTPUT):
        shutil.rmtree(TFJS_OUTPUT)
    os.makedirs(TFJS_OUTPUT)

    print("Converting model to TF.js format…")
    result = subprocess.run(
        [
            sys.executable, "-m", "tensorflowjs.converters.converter",
            "--input_format=keras",
            MODEL_H5,
            TFJS_OUTPUT,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Conversion failed:\n{result.stderr}")

    # ── Write class_labels.json (MY ADDITION) ─────────────
    class_names            = get_classes()
    display_names, descriptions = load_labels()

    labels_data = {
        "class_names":   class_names,
        "display_names": {k: display_names.get(k, k) for k in class_names},
        "descriptions":  {k: descriptions.get(k, "")  for k in class_names},
    }
    labels_path = os.path.join(TFJS_OUTPUT, "class_labels.json")
    with open(labels_path, "w") as f:
        json.dump(labels_data, f, indent=2)

    print(f"class_labels.json written for {len(class_names)} classes.")

    # ── ZIP ────────────────────────────────────────────────
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in os.listdir(TFJS_OUTPUT):
            zf.write(os.path.join(TFJS_OUTPUT, fname), fname)

    print(f"ZIP created: {ZIP_OUTPUT}")
    return TFJS_OUTPUT


if __name__ == "__main__":
    try:
        convert()
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)"""
convert_model.py
Converts backend/saved_model/best_model.h5 → TF.js LayersModel format.
Also writes class_labels.json into the output so the download ZIP
contains everything the frontend needs.

Usage:
    python convert_model.py          (standalone)
    from convert_model import convert  (called by app.py after training)
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess

from database import BACKEND_DIR, get_classes, load_labels

MODEL_H5    = os.path.join(BACKEND_DIR, "saved_model", "best_model.h5")
TFJS_OUTPUT = os.path.join(BACKEND_DIR, "tfjs_model")
ZIP_OUTPUT  = os.path.join(BACKEND_DIR, "tfjs_model.zip")


def convert() -> str:
    """
    Converts .h5 → TF.js, writes class_labels.json, zips everything.
    Returns path to the TFJS output directory.
    Raises RuntimeError on failure.
    """
    if not os.path.exists(MODEL_H5):
        raise RuntimeError(f"Model not found at {MODEL_H5}. Run training first.")

    # Clean and recreate output dir
    if os.path.exists(TFJS_OUTPUT):
        shutil.rmtree(TFJS_OUTPUT)
    os.makedirs(TFJS_OUTPUT)

    print("Converting model to TF.js format…")
    result = subprocess.run(
        [
            sys.executable, "-m", "tensorflowjs.converters.converter",
            "--input_format=keras",
            MODEL_H5,
            TFJS_OUTPUT,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Conversion failed:\n{result.stderr}")

    # ── Write class_labels.json (MY ADDITION) ─────────────
    class_names            = get_classes()
    display_names, descriptions = load_labels()

    labels_data = {
        "class_names":   class_names,
        "display_names": {k: display_names.get(k, k) for k in class_names},
        "descriptions":  {k: descriptions.get(k, "")  for k in class_names},
    }
    labels_path = os.path.join(TFJS_OUTPUT, "class_labels.json")
    with open(labels_path, "w") as f:
        json.dump(labels_data, f, indent=2)

    print(f"class_labels.json written for {len(class_names)} classes.")

    # ── ZIP ────────────────────────────────────────────────
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in os.listdir(TFJS_OUTPUT):
            zf.write(os.path.join(TFJS_OUTPUT, fname), fname)

    print(f"ZIP created: {ZIP_OUTPUT}")
    return TFJS_OUTPUT


if __name__ == "__main__":
    try:
        convert()
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)