"""
app.py
Flask REST API — Admin Panel backend.

Endpoints:
    GET  /classes          → list classes + display names
    POST /add_class        → create new class folder
    GET  /image_counts     → images per class
    POST /upload_images    → upload training images to a class
    POST /train            → start training, streams log lines
    GET  /download_model   → download tfjs_model.zip

Run: python app.py
"""

import threading
import queue
import os

from flask import Flask, jsonify, request, Response, send_file
from flask_cors import CORS

from database import (
    ensure_dataset_dir,
    get_classes,
    add_class,
    save_images,
    get_image_counts,
    load_labels,
)
from train       import run_training
from convert_model import convert, ZIP_OUTPUT

app = Flask(__name__)
CORS(app)  # Allow React dev server and deployed site to call this API

ensure_dataset_dir()

# ── Classes ────────────────────────────────────────────────

@app.route("/classes", methods=["GET"])
def list_classes():
    classes = get_classes()
    display, _ = load_labels()
    return jsonify({"classes": classes, "display_names": display})


@app.route("/add_class", methods=["POST"])
def create_class():
    body         = request.get_json(silent=True) or {}
    folder_name  = str(body.get("folder_name", "")).strip()
    display_name = str(body.get("display_name", "")).strip() or folder_name
    description  = str(body.get("description", "")).strip()

    if not folder_name:
        return jsonify({"success": False, "error": "folder_name is required."}), 400

    # Sanitise: only alphanumerics + underscore
    import re
    if not re.match(r'^[a-z0-9_]+$', folder_name):
        return jsonify({"success": False, "error": "folder_name must be lowercase alphanumeric with underscores only."}), 400

    success, msg = add_class(folder_name, display_name, description)
    status = 200 if success else 400
    return jsonify({"success": success, "message": msg if success else None, "error": msg if not success else None}), status


@app.route("/image_counts", methods=["GET"])
def image_counts():
    return jsonify(get_image_counts())

# ── Upload ─────────────────────────────────────────────────

@app.route("/upload_images", methods=["POST"])
def upload_images():
    class_name = request.form.get("class_name", "").strip()
    files      = request.files.getlist("images")

    if not class_name:
        return jsonify({"success": False, "error": "class_name is required."}), 400
    if not files or files[0].filename == "":
        return jsonify({"success": False, "error": "No files received."}), 400

    # Validate class exists
    if class_name not in get_classes():
        return jsonify({"success": False, "error": f"Class '{class_name}' does not exist."}), 400

    count = save_images(class_name, files)
    return jsonify({"success": True, "message": f"{count} image(s) saved to '{class_name}'."})

# ── Training (streaming) ───────────────────────────────────

def _training_generator():
    """Runs training in a thread; yields log lines as they arrive."""
    q = queue.Queue()

    def _thread():
        try:
            ok = run_training(log_callback=lambda msg: q.put(msg))
            if ok:
                q.put("Converting model to TF.js…\n")
                try:
                    convert()
                    q.put("Training complete. Model is ready for download.\n")
                except Exception as e:
                    q.put(f"Conversion error: {e}\n")
        except Exception as e:
            q.put(f"FATAL: {e}\n")
        finally:
            q.put(None)  # Sentinel

    t = threading.Thread(target=_thread, daemon=True)
    t.start()

    while True:
        msg = q.get()
        if msg is None:
            break
        yield msg


@app.route("/train", methods=["POST"])
def start_training():
    return Response(_training_generator(), mimetype="text/plain")

# ── Model Download ─────────────────────────────────────────

@app.route("/download_model", methods=["GET"])
def download_model():
    if not os.path.exists(ZIP_OUTPUT):
        return jsonify({"error": "No model ZIP found. Train the model first."}), 404
    return send_file(ZIP_OUTPUT, as_attachment=True, download_name="tfjs_model.zip")

# ── Entry ──────────────────────────────────────────────────

if __name__ == "__main__":
    print("Admin API running at http://localhost:5000")
    app.run(debug=True, port=5000, threaded=True)