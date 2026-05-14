export default function LoadingSpinner({ text = 'Loading…' }) {
  return (
    <div className="loading-box">
      <div className="spinner" />
      <p className="loading-text">{text}</p>
    </div>
  );
}