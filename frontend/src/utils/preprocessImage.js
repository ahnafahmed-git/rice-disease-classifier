/**
 * preprocessImage.js
 * Converts an HTMLImageElement → a preprocessed tensor
 * matching the MobileNetV2 training pipeline exactly:
 *   resize to 224×224 → scale [0,255] to [-1,1]
 */

import * as tf from '@tensorflow/tfjs';

const IMG_SIZE = 224;

/**
 * @param {HTMLImageElement} imgElement
 * @returns {tf.Tensor4D}  shape [1, 224, 224, 3], dtype float32, range [-1, 1]
 */
export function preprocessImage(imgElement) {
  return tf.tidy(() => {
    const tensor = tf.browser
      .fromPixels(imgElement)             // [H, W, 3], uint8
      .resizeBilinear([IMG_SIZE, IMG_SIZE]) // [224, 224, 3]
      .toFloat();                           // float32

    // MobileNetV2 preprocess_input: pixel/127.5 - 1
    const normalised = tensor.div(127.5).sub(1.0);
    return normalised.expandDims(0);        // [1, 224, 224, 3]
  });
}