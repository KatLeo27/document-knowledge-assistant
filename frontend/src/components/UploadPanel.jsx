import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Loader2, AlertCircle } from 'lucide-react';
import DocumentCard from './DocumentCard';

export default function UploadPanel({
  documents,
  isUploading,
  onUploadFile,
  onRequestDelete,
  deletingDoc,
}) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      onUploadFile(file);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      onUploadFile(file);
      e.target.value = ''; // Reset input
    }
  };

  return (
    <aside className="right-panel">
      {/* Upload Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div className="panel-header">
          <span className="panel-title">Upload Documents</span>
        </div>

        <div
          className={`upload-dropzone ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !isUploading && fileInputRef.current?.click()}
          style={{ opacity: isUploading ? 0.7 : 1, cursor: isUploading ? 'not-allowed' : 'pointer' }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            className="upload-file-input"
            onChange={handleFileChange}
            disabled={isUploading}
          />

          <div className="upload-icon-wrap">
            {isUploading ? (
              <Loader2 size={22} className="spin-anim" />
            ) : (
              <UploadCloud size={22} />
            )}
          </div>

          <div>
            <p className="upload-title">
              {isUploading ? 'Indexing PDF document...' : 'Drop your PDF here'}
            </p>
            <p className="upload-subtitle">
              {isUploading ? 'Chunking & generating embeddings' : 'or click to browse · PDF only'}
            </p>
          </div>
        </div>
      </div>

      {/* Document List Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1 }}>
        <div className="panel-header">
          <span className="panel-title">Your Documents</span>
          <span className="panel-count">{documents.length}</span>
        </div>

        <div className="doc-list">
          {documents.length === 0 ? (
            <div className="doc-list-empty">
              <FileText size={28} style={{ opacity: 0.3, margin: '0 auto 8px auto' }} />
              <p>No documents indexed yet.</p>
              <p style={{ fontSize: '0.75rem', marginTop: '4px', opacity: 0.7 }}>
                Upload a PDF above to begin.
              </p>
            </div>
          ) : (
            documents.map((doc, idx) => (
              <DocumentCard
                key={doc.source}
                doc={doc}
                index={idx}
                onRequestDelete={onRequestDelete}
                isDeleting={deletingDoc === doc.source}
              />
            ))
          )}
        </div>
      </div>
    </aside>
  );
}
