import { useState }    from 'react';
import { useModel }    from '../hooks/useModel';
import ImageUploader   from '../components/ImageUploader';
import ResultCard      from '../components/ResultCard';
import LoadingSpinner  from '../components/LoadingSpinner';
import { preprocessImage }  from '../utils/preprocessImage';


export default function Home() {
  const { model, classLabels, modelLoading, modelError } = useModel();

  const [imgEl,      setImgEl]      = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [result,     setResult]     = useState(null);

  function handleImageReady(img) {
    setImgEl(img);
    setResult(null);   // Clear previous result when new image is uploaded
  }

  async function handleClassify() {
    if (!model || !imgEl) return;
    setPredicting(true);
    setResult(null);

    try {
      const tensor     = preprocessImage(imgEl);
      const predTensor = model.predict(tensor);
      const scores     = Array.from(await predTensor.data());
      predTensor.dispose();
      tensor.dispose();

      // Replace the riceLeafChecker import and usage with this logic:

      const maxIdx     = scores.indexOf(Math.max(...scores));
      const confidence = scores[maxIdx];
      const className  = classLabels.class_names[maxIdx];

      // Model itself tells us if it's not a rice leaf
      const isRiceLeaf = className !== 'non_rice_leaf' && confidence >= 0.35;
      const reason     = !isRiceLeaf
        ? className === 'non_rice_leaf'
          ? 'The uploaded image does not appear to be a rice leaf.'
          : `Confidence too low (${(confidence * 100).toFixed(1)}%). Try a clearer image.`
        : '';

      setResult({ className, confidence, isRiceLeaf, reason });

    } catch (err) {
      setResult({
        className:   null,
        confidence:  0,
        isRiceLeaf:  false,
        reason:      `Prediction failed: ${err.message}`,
      });
    } finally {
      setPredicting(false);
    }
  }

  // ── Error state ──────────────────────────────────────────
  if (modelError) {
    return (
      <main className="page">
        <div className="card">
          <div className="alert alert-error">
            ❌ Failed to load model: {modelError}
            <br />
            <small>
              Make sure <code>public/model/model.json</code> exists.
              Run <code>python scripts/convert_for_web.py</code> first.
            </small>
          </div>
        </div>
      </main>
    );
  }

  // ── Main ─────────────────────────────────────────────────
  return (
    <main className="page">
      <div className="card">
        <h1 className="page-title">Rice Leaf Disease Classifier</h1>
        <p className="page-subtitle">
          Upload a clear photograph of a rice leaf. The model will identify
          any disease present from {classLabels.class_names.length} known classes.
        </p>

        {modelLoading ? (
          <LoadingSpinner text="Loading classification model…" />
        ) : (
          <>
            <ImageUploader onImageReady={handleImageReady} />
            <button
              className="btn btn-primary btn-full"
              onClick={handleClassify}
              disabled={!imgEl || predicting}
            >
              {predicting ? 'Classifying…' : 'Classify Image'}
            </button>
          </>
        )}
      </div>

      {predicting && (
        <div className="card">
          <LoadingSpinner text="Running inference…" />
        </div>
      )}

      {result && !predicting && (
        <ResultCard result={result} classLabels={classLabels} />
      )}
    </main>
  );
}