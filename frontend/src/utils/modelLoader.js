/**
 * modelLoader.js
 * Loads the TF.js LayersModel from public/model/model.json.
 * Model is cached after first load to avoid repeated network requests.
 */

import * as tf from '@tensorflow/tfjs';

const MODEL_URL = `${import.meta.env.BASE_URL}model/model.json`;

let _cachedModel = null;

/**
 * @returns {Promise<tf.LayersModel>}
 */
export async function loadModel() {
  if (_cachedModel) return _cachedModel;
  _cachedModel = await tf.loadGraphModel(MODEL_URL);
  return _cachedModel;
}

export function disposeModel() {
  if (_cachedModel) {
    _cachedModel.dispose();
    _cachedModel = null;
  }
}