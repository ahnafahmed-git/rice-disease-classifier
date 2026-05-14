# scripts/prepare_non_rice_leaf.py
# Flattens all animal subfolders into one non_rice_leaf folder.
# Run from project root: python scripts/prepare_non_rice_leaf.py

import os, shutil

RAW_DIR = r"C:\Users\ahmed\Downloads\non_rice_leaf_images\raw-img"          # ← change to your raw-img path
OUT_DIR = r"D:\Projects\non_rice_leaf"  # ← output folder (upload this to Drive)

MAX_IMAGES = 300

os.makedirs(OUT_DIR, exist_ok=True)

count = 0
for animal_folder in os.listdir(RAW_DIR):
    if count >= MAX_IMAGES:
        break
    src = os.path.join(RAW_DIR, animal_folder)
    if not os.path.isdir(src):
        continue
    for fname in os.listdir(src):
        if count >= MAX_IMAGES:
            break
        if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        new_name = f"{animal_folder}_{count:05d}{os.path.splitext(fname)[1]}"
        shutil.copy(os.path.join(src, fname), os.path.join(OUT_DIR, new_name))
        count += 1

print(f"Done. {count} images copied to {OUT_DIR}")