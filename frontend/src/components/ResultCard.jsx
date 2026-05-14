/**
 * ResultCard
 * Renders classification output or a rejection warning.
 * Accepts classLabels from useModel() so display names are always in sync.
 */
export default function ResultCard({ result, classLabels }) {
  if (!result) return null;

  const { className, confidence, isRiceLeaf, reason } = result;

  if (!isRiceLeaf) {
    return (
      <div className="card">
        <div className="alert alert-warning">⚠️ {reason}</div>
      </div>
    );
  }

  const pct         = (confidence * 100).toFixed(1);
  const displayName = classLabels?.display_names?.[className] ?? className;
  const description = classLabels?.descriptions?.[className]  ?? '';

  // Colour the bar amber if confidence < 60%, green otherwise
  const barColor = confidence < 0.60 ? '#d97706' : 'var(--accent)';

  return (
    <div className="card">
      <p className="result-label">Predicted Disease</p>
      <p className="result-value">{displayName}</p>
      <p className="result-confidence">Confidence: {pct}%</p>

      <div className="confidence-bar-track">
        <div
          className="confidence-bar-fill"
          style={{ width: `${pct}%`, background: barColor }}
        />
      </div>

      {description && (
        <p className="result-description">{description}</p>
      )}
    </div>
  );
}