/**
 * useModel.js
 * Loads TF.js model AND class labels in parallel.
 * Exposes { model, classLabels, modelLoading, modelError }.
 */

import { useState, useEffect } from 'react';
import { loadModel }        from '../utils/modelLoader';
import { fetchClassLabels, FALLBACK_LABELS } from '../utils/classLabels';

export function useModel() {
  const [model,        setModel]        = useState(null);
  const [classLabels,  setClassLabels]  = useState(FALLBACK_LABELS);
  const [modelLoading, setModelLoading] = useState(true);
  const [modelError,   setModelError]   = useState(null);

  useEffect(() => {
    let cancelled = false;
    setModelLoading(true);

    Promise.all([loadModel(), fetchClassLabels()])
      .then(([m, labels]) => {
        if (cancelled) return;
        setModel(m);
        setClassLabels(labels);
        setModelLoading(false);
      })
      .catch((err) => {
        if (cancelled) return;
        setModelError(err.message);
        setModelLoading(false);
      });

    return () => { cancelled = true; };
  }, []);

  return { model, classLabels, modelLoading, modelError };
}