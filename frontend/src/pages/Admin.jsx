/**
 * Admin.jsx
 * Password-gated panel for:
 *   - Viewing current classes and image counts
 *   - Adding new disease classes
 *   - Uploading training images
 *   - Triggering retraining with live log streaming
 *   - Downloading the new TF.js model after training
 *
 * Requires the Flask backend (backend/app.py) running on localhost:5000.
 */

import { useState, useEffect, useRef } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import { FALLBACK_LABELS } from '../utils/classLabels';

// ── Config ────────────────────────────────────────────────
// Change this password or move it to an env variable
const ADMIN_PASSWORD = 'admin1234';
const API_BASE       = 'http://localhost:5000';

export default function Admin() {
  const [authed,  setAuthed]  = useState(false);
  const [pw,      setPw]      = useState('');
  const [pwError, setPwError] = useState('');

  // State after login
  const [classes,    setClasses]    = useState([]);
  const [imgCounts,  setImgCounts]  = useState({});
  const [displayNames, setDisplayNames] = useState(FALLBACK_LABELS.display_names);
  const [fetchError, setFetchError] = useState('');

  // Add new class
  const [newFolder,  setNewFolder]  = useState('');
  const [newDisplay, setNewDisplay] = useState('');

  // Upload images
  const [selectedClass, setSelectedClass]   = useState('');
  const [uploadFiles,   setUploadFiles]     = useState([]);
  const [uploading,     setUploading]       = useState(false);

  // Training
  const [training, setTraining] = useState(false);
  const [log,      setLog]      = useState('');
  const logRef = useRef(null);

  // Status message
  const [status, setStatus] = useState(null); // { type, text }

  // ── Auth ───────────────────────────────────────────────
  function handleLogin() {
    if (pw === ADMIN_PASSWORD) {
      setAuthed(true);
      setPwError('');
    } else {
      setPwError('Incorrect password.');
    }
  }

  // ── Data fetch after login ─────────────────────────────
  useEffect(() => {
    if (!authed) return;
    fetchData();
  }, [authed]);

  async function fetchData() {
    try {
      const [classRes, countRes] = await Promise.all([
        fetch(`${API_BASE}/classes`),
        fetch(`${API_BASE}/image_counts`),
      ]);
      const classData = await classRes.json();
      const countData = await countRes.json();
      setClasses(classData.classes);
      setDisplayNames(classData.display_names);
      setImgCounts(countData);
      setFetchError('');
    } catch {
      setFetchError(
        'Could not reach backend. Start it with: cd backend && python app.py'
      );
    }
  }

  // ── Add class ──────────────────────────────────────────
  async function handleAddClass() {
    const folder  = newFolder.trim().toLowerCase().replace(/\s+/g, '_');
    const display = newDisplay.trim() || folder;
    if (!folder) return;

    try {
      const res  = await fetch(`${API_BASE}/add_class`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ folder_name: folder, display_name: display }),
      });
      const data = await res.json();
      if (data.success) {
        setStatus({ type: 'success', text: `Class '${display}' added successfully.` });
        setNewFolder('');
        setNewDisplay('');
        fetchData();
      } else {
        setStatus({ type: 'error', text: data.error });
      }
    } catch {
      setStatus({ type: 'error', text: 'Backend unreachable.' });
    }
  }

  // ── Upload images ──────────────────────────────────────
  async function handleUpload() {
    if (!selectedClass || uploadFiles.length === 0) return;
    setUploading(true);
    const form = new FormData();
    form.append('class_name', selectedClass);
    for (const f of uploadFiles) form.append('images', f);

    try {
      const res  = await fetch(`${API_BASE}/upload_images`, { method: 'POST', body: form });
      const data = await res.json();
      setStatus({
        type: data.success ? 'success' : 'error',
        text: data.message ?? data.error,
      });
      if (data.success) fetchData();
    } catch {
      setStatus({ type: 'error', text: 'Backend unreachable.' });
    } finally {
      setUploading(false);
      setUploadFiles([]);
    }
  }

  // ── Train ──────────────────────────────────────────────
  async function handleTrain() {
    setTraining(true);
    setLog('Connecting to training server…\n');

    try {
      const res    = await fetch(`${API_BASE}/train`, { method: 'POST' });
      const reader = res.body.getReader();
      const dec    = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = dec.decode(value);
        setLog((prev) => {
          const next = prev + chunk;
          // Auto-scroll the log box
          setTimeout(() => {
            if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
          }, 0);
          return next;
        });
      }
      setStatus({ type: 'success', text: 'Training complete. Download the model below and replace public/model/.' });
    } catch (e) {
      setStatus({ type: 'error', text: `Training error: ${e.message}` });
    } finally {
      setTraining(false);
    }
  }

  // ── Password Gate ──────────────────────────────────────
  if (!authed) {
    return (
      <main className="page">
        <div className="card password-gate">
          <h2 className="section-title">Admin Panel</h2>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              className="form-input"
              type="password"
              value={pw}
              onChange={(e) => setPw(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
              placeholder="Enter admin password"
              autoFocus
            />
          </div>
          {pwError && <div className="alert alert-error" style={{ marginBottom: '0.75rem' }}>{pwError}</div>}
          <button className="btn btn-primary btn-full" onClick={handleLogin}>
            Login
          </button>
        </div>
      </main>
    );
  }

  // ── Admin UI ───────────────────────────────────────────
  return (
    <main className="page">
      <h1 className="page-title" style={{ marginBottom: '1.5rem' }}>Admin Panel</h1>

      {/* Status banner */}
      {status && (
        <div className={`alert alert-${status.type}`} style={{ marginBottom: '1.25rem' }}>
          {status.text}
          <button className="alert-dismiss" onClick={() => setStatus(null)}>✕</button>
        </div>
      )}

      {/* Backend offline warning */}
      {fetchError && (
        <div className="alert alert-warning" style={{ marginBottom: '1.25rem' }}>
          ⚠️ {fetchError}
        </div>
      )}

      {/* ── Current Classes & Image Counts ─────────────── */}
      <div className="card">
        <p className="section-title">Dataset Overview</p>
        {classes.length === 0 ? (
          <LoadingSpinner text="Loading classes…" />
        ) : (
          <table className="img-count-table">
            <thead>
              <tr>
                <th>Class</th>
                <th>Folder</th>
                <th style={{ textAlign: 'right' }}>Images</th>
              </tr>
            </thead>
            <tbody>
              {classes.map((c) => (
                <tr key={c}>
                  <td>{displayNames[c] ?? c}</td>
                  <td style={{ color: 'var(--text-muted)', fontFamily: 'monospace', fontSize: '0.8rem' }}>{c}</td>
                  <td style={{ textAlign: 'right' }}>{imgCounts[c] ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <button className="btn btn-secondary" style={{ marginTop: '1rem' }} onClick={fetchData}>
          ↺ Refresh
        </button>
      </div>

      {/* ── Add New Class ───────────────────────────────── */}
      <div className="card">
        <p className="section-title">Add New Disease Class</p>
        <div className="form-group">
          <label className="form-label">Folder Name <span style={{ color: 'var(--text-muted)' }}>(snake_case, e.g. sheath_blight)</span></label>
          <input
            className="form-input"
            value={newFolder}
            onChange={(e) => setNewFolder(e.target.value)}
            placeholder="sheath_blight"
          />
        </div>
        <div className="form-group">
          <label className="form-label">Display Name <span style={{ color: 'var(--text-muted)' }}>(shown in UI, e.g. Sheath Blight)</span></label>
          <input
            className="form-input"
            value={newDisplay}
            onChange={(e) => setNewDisplay(e.target.value)}
            placeholder="Sheath Blight"
          />
        </div>
        <button
          className="btn btn-secondary"
          onClick={handleAddClass}
          disabled={!newFolder.trim()}
        >
          ＋ Add Class
        </button>
      </div>

      {/* ── Upload Training Images ──────────────────────── */}
      <div className="card">
        <p className="section-title">Upload Training Images</p>
        <div className="form-group">
          <label className="form-label">Target Class</label>
          <select
            className="form-input"
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
          >
            <option value="">— select a class —</option>
            {classes.map((c) => (
              <option key={c} value={c}>{displayNames[c] ?? c}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">
            Images {uploadFiles.length > 0 && `(${uploadFiles.length} selected)`}
          </label>
          <input
            type="file"
            accept="image/*"
            multiple
            className="form-input"
            onChange={(e) => setUploadFiles([...e.target.files])}
          />
        </div>
        <button
          className="btn btn-secondary"
          onClick={handleUpload}
          disabled={uploading || !selectedClass || uploadFiles.length === 0}
        >
          {uploading ? 'Uploading…' : '⬆ Upload Images'}
        </button>
      </div>

      {/* ── Train / Retrain ─────────────────────────────── */}
      <div className="card">
        <p className="section-title">Train / Retrain Model</p>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem', lineHeight: 1.6 }}>
          Retrains MobileNetV2 on all images currently in the dataset, including any
          newly added classes. After training completes, download the converted
          TF.js model ZIP and extract its contents into <code>public/model/</code>,
          then rebuild and redeploy.
        </p>

        <button
          className="btn btn-primary"
          onClick={handleTrain}
          disabled={training}
        >
          {training ? '⏳ Training in progress…' : '▶ Start Training'}
        </button>

        {(log || training) && (
          <div className="training-log" ref={logRef}>
            {log || 'Initialising…'}
          </div>
        )}

        {!training && log.includes('Training complete') && (
          <a
          href={API_BASE + '/download_model'}
          className="btn btn-secondary"
          style={{ marginTop: '0.75rem', display: 'inline-flex' }}
          download
        >
          ⬇ Download TF.js Model ZIP
        </a>
      )}
      </div>
    </main>
  );
}