"""
convert_for_web.py
One-command pipeline:
    1. Converts backend/saved_model/best_model.h5 → TF.js LayersModel
    2. Copies the output into frontend/public/model/
       (replaces previous model files)

Run from project root after training:
    python scripts/convert_for_web.py
"""

import os
import sys
import shutil

PROJECT_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR    = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_MODEL = os.path.join(PROJECT_ROOT, "frontend", "public", "model")

# Add backend to path so we can import convert_model
sys.path.insert(0, BACKEND_DIR)
from convert_model import convert, TFJS_OUTPUT


def main():
    print("Step 1: Converting model to TF.js format…")
    try:
        tfjs_dir = convert()
    except RuntimeError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nStep 2: Copying to frontend/public/model/ …")
    if os.path.exists(FRONTEND_MODEL):
        shutil.rmtree(FRONTEND_MODEL)
    shutil.copytree(tfjs_dir, FRONTEND_MODEL)

    # List copied files
    for f in os.listdir(FRONTEND_MODEL):
        print(f"  ✓ {f}")

    print(
        "\nDone. The frontend model is updated.\n"
        "Run 'npm run build && npm run deploy' inside frontend/ to redeploy."
    )


if __name__ == "__main__":
    main()