import { useRef, useState } from 'react';

/**
 * ImageUploader
 * Accepts a file via click or drag-and-drop.
 * Calls onImageReady(HTMLImageElement) once the image is loaded.
 */
export default function ImageUploader({ onImageReady }) {
  const inputRef  = useRef(null);
  const [preview, setPreview]  = useState(null);
  const [dragOver, setDragOver] = useState(false);

  function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) return;
    const url = URL.createObjectURL(file);
    setPreview(url);

    const img = new Image();
    img.src = url;
    img.onload = () => onImageReady(img);
  }

  function onChange(e)  { handleFile(e.target.files[0]); }

  function onDrop(e) {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  }

  return (
    <div>
      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
        onClick={() => inputRef.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current.click()}
        aria-label="Image upload area"
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={onChange}
          aria-hidden="true"
        />
        <div className="upload-icon">📂</div>
        <p className="upload-label">Click or drag &amp; drop an image here</p>
        <p className="upload-hint">Supports JPG · PNG · WEBP</p>
      </div>

      {preview && (
        <img
          src={preview}
          alt="Uploaded preview"
          className="preview-img"
        />
      )}
    </div>
  );
}