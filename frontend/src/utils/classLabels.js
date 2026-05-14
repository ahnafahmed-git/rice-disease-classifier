/**
 * classLabels.js
 * Fetches class metadata from public/model/class_labels.json at runtime.
 * This means class names update automatically after a retrain + model replacement
 * without requiring a source code change or rebuild.
 *
 * MY ADDITION: runtime JSON fetch instead of hardcoded constants,
 * enabling future class expansion with zero code changes.
 */

const LABELS_URL = `${import.meta.env.BASE_URL}model/class_labels.json`;

let _cache = null;

/**
 * Fetches and caches the class labels JSON.
 * @returns {Promise<{class_names: string[], display_names: object, descriptions: object}>}
 */
export async function fetchClassLabels() {
  if (_cache) return _cache;
  const res = await fetch(LABELS_URL);
  if (!res.ok) throw new Error(`Failed to load class_labels.json (${res.status})`);
  _cache = await res.json();
  return _cache;
}

/** Fallback used before fetch completes or if it fails. */
export const FALLBACK_LABELS = {
  class_names: [
    "bacterial_leaf_blight",
    "brown_spot",
    "healthy",
    "leaf_blast",
    "leaf_scald",
    "narrow_brown_spot",
  ],
  display_names: {
    bacterial_leaf_blight: "Bacterial Leaf Blight",
    brown_spot:            "Brown Spot",
    healthy:               "Healthy",
    leaf_blast:            "Leaf Blast",
    leaf_scald:            "Leaf Scald",
    narrow_brown_spot:     "Narrow Brown Spot",
  },
  descriptions: {},
};