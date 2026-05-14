"""
train.py
MobileNetV2 fine-tuning pipeline — mirrors the original architecture exactly,
with additions for:
  - Dynamic class count (new classes handled automatically)
  - Weight transfer when class count changes (preserves base + intermediate layers)
  - Streaming log callback for Flask's /train endpoint
  - Standalone execution: python train.py
"""

import os
import sys
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from database import DATASET_DIR, BACKEND_DIR, get_classes

# ── Hyperparameters (match original) ─────────────────────
IMG_SIZE    = (224, 224)
BATCH_SIZE  = 32
EPOCHS      = 20

SAVED_MODEL_DIR  = os.path.join(BACKEND_DIR, "saved_model")
MODEL_SAVE_PATH  = os.path.join(SAVED_MODEL_DIR, "best_model.h5")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


# ── Dataset loading ───────────────────────────────────────

def load_dataset(class_names):
    paths, labels = [], []
    for idx, cls in enumerate(class_names):
        cls_dir = os.path.join(DATASET_DIR, cls)
        if not os.path.isdir(cls_dir):
            continue
        for fname in os.listdir(cls_dir):
            if os.path.splitext(fname)[1].lower() in IMAGE_EXTS:
                paths.append(os.path.join(cls_dir, fname))
                labels.append(idx)
    return np.array(paths), np.array(labels)


def process_image(path, label, num_classes):
    """Mirrors original pipeline: decode → resize → MobileNetV2 preprocess → one-hot."""
    image = tf.io.read_file(path)
    image = tf.image.decode_image(image, channels=3, expand_animations=False)
    image = tf.image.resize(image, IMG_SIZE)
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    return image, tf.one_hot(label, depth=num_classes)


def build_tf_dataset(paths, labels, num_classes, shuffle=True):
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(
        lambda p, l: process_image(p, l, num_classes),
        num_parallel_calls=tf.data.AUTOTUNE,
    )
    if shuffle:
        ds = ds.shuffle(buffer_size=512)
    return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)


# ── Model construction ────────────────────────────────────

def build_model(num_classes):
    """Builds MobileNetV2 model — identical to original architecture."""
    base = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet',
    )
    base.trainable = False  # Freeze convolutional base

    model = tf.keras.Sequential([
        base,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(num_classes, activation='softmax'),
    ])
    return model


def load_or_build_model(num_classes, log):
    """
    MY ADDITION: Attempts to load existing weights.
    If class count changed, transfers all layers except the final Dense
    so training resumes from a strong baseline rather than scratch.
    """
    model = build_model(num_classes)

    if os.path.exists(MODEL_SAVE_PATH):
        try:
            old = tf.keras.models.load_model(MODEL_SAVE_PATH)
            old_classes = old.layers[-1].units

            if old_classes == num_classes:
                model.set_weights(old.get_weights())
                log("[INFO] Loaded existing model weights (class count unchanged).")
            else:
                log(f"[INFO] Class count changed ({old_classes} → {num_classes}). Transferring compatible weights.")
                # Transfer all layers except the final Dense (index -1)
                for new_l, old_l in zip(model.layers[:-1], old.layers[:-1]):
                    try:
                        new_l.set_weights(old_l.get_weights())
                    except Exception:
                        pass
                log("[INFO] Weight transfer complete. Final Dense layer reinitialized.")
        except Exception as e:
            log(f"[WARN] Could not load existing model ({e}). Starting from ImageNet weights.")
    else:
        log("[INFO] No saved model found. Starting from ImageNet weights.")

    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )
    return model


# ── Training ──────────────────────────────────────────────

def run_training(log_callback=None):
    """
    Main entry point. log_callback(str) is called for each log line.
    Returns True on success, False on failure.
    """
    def log(msg):
        full = str(msg) + "\n"
        if log_callback:
            log_callback(full)
        else:
            print(msg, flush=True)

    class_names  = get_classes()
    num_classes  = len(class_names)
    log(f"Classes ({num_classes}): {class_names}")

    paths, labels = load_dataset(class_names)
    log(f"Total images found: {len(paths)}")

    if len(paths) < num_classes * 2:
        log("ERROR: Not enough images. Each class needs at least 2 images.")
        return False

    # Check every class has at least 1 sample (required for stratify)
    from collections import Counter
    counts = Counter(labels)
    for idx, cls in enumerate(class_names):
        if counts.get(idx, 0) < 2:
            log(f"ERROR: Class '{cls}' has fewer than 2 images. Add more images before training.")
            return False

    train_paths, val_paths, train_labels, val_labels = train_test_split(
        paths, labels, test_size=0.2, stratify=labels, random_state=42
    )
    log(f"Split → Train: {len(train_paths)} | Val: {len(val_paths)}")

    train_ds = build_tf_dataset(train_paths, train_labels, num_classes, shuffle=True)
    val_ds   = build_tf_dataset(val_paths,   val_labels,   num_classes, shuffle=False)

    os.makedirs(SAVED_MODEL_DIR, exist_ok=True)
    model = load_or_build_model(num_classes, log)

    class _StreamLogger(tf.keras.callbacks.Callback):
        def on_epoch_end(self, epoch, logs=None):
            log(
                f"Epoch {epoch + 1:>2}/{EPOCHS} — "
                f"loss: {logs['loss']:.4f}  acc: {logs['accuracy']:.4f}  "
                f"val_loss: {logs['val_loss']:.4f}  val_acc: {logs['val_accuracy']:.4f}"
            )

    log("Model built. Training started…\n")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=[
            tf.keras.callbacks.ModelCheckpoint(
                MODEL_SAVE_PATH, save_best_only=True, verbose=0
            ),
            tf.keras.callbacks.ReduceLROnPlateau(patience=5, factor=0.1, verbose=0),
            _StreamLogger(),
        ],
        verbose=0,
    )

    log(f"\nTraining complete. Best model saved to:\n  {MODEL_SAVE_PATH}")
    return True


if __name__ == "__main__":
    run_training()