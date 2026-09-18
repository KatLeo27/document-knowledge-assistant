import React, { useState, useRef } from 'react';
import {
  FileText,
  Search,
  UploadCloud,
  Trash2,
  MessageSquare,
  Layers,
  Sparkles,
  Loader2,
  Database,
  ArrowRight,
} from 'lucide-react';

const COLOR_VARIANTS = ['rose', 'sage', 'lavender', 'butter'];

export default function DocumentArchiveView({
  documents,
  isUploading,
  onUploadFile,
  onRequestDelete,
  deletingDoc,
  onAskAboutDoc,
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const filteredDocs = documents.filter((d) =>
    d.source.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalChunks = documents.reduce((acc, d) => acc + (d.chunk_count || 0), 0);
  const avgChunks = documents.length > 0 ? Math.round(totalChunks / documents.length) : 0;

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
      onUploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onUploadFile(e.target.files[0]);
      e.target.value = '';
    }
  };

  return (
    <div className="archive-view">
      {/* Archive Header Banner */}
      <div className="archive-header-card">
        <div>
          <div className="hero-badge" style={{ marginBottom: '10px' }}>
            <FileText size={14} />
            <span>Document Repository</span>
          </div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            Document Archive
          </h2>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Explore, manage, and query all indexed PDF documents stored in your ChromaDB vector collection.
          </p>
        </div>

        <button
          className="theme-toggle-btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          style={{
            backgroundColor: 'var(--sage-green-light)',
            borderColor: 'var(--sage-green-border)',
            color: 'var(--sage-green-text)',
            padding: '10px 20px',
            fontSize: '0.9rem',
          }}
        >
          {isUploading ? (
            <>
              <Loader2 size={16} className="spin-anim" />
              <span>Indexing PDF...</span>
            </>
          ) : (
            <>
              <UploadCloud size={16} />
              <span>Upload New PDF</span>
            </>
          )}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
      </div>

      {/* Stats Summary Row */}
      <div className="archive-stats-row">
        <div className="archive-stat-box">
          <div className="feature-icon-wrap sage">
            <FileText size={20} />
          </div>
          <div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              {documents.length}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              Indexed Documents
            </div>
          </div>
        </div>

        <div className="archive-stat-box">
          <div className="feature-icon-wrap rose">
            <Layers size={20} />
          </div>
          <div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              {totalChunks}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              Total Vector Chunks
            </div>
          </div>
        </div>

        <div className="archive-stat-box">
          <div className="feature-icon-wrap lavender">
            <Database size={20} />
          </div>
          <div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              {avgChunks}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              Avg. Chunks / Doc
            </div>
          </div>
        </div>
      </div>

      {/* Search & Upload Container */}
      <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
        <div className="search-input-box" style={{ flex: 1 }}>
          <Search size={18} style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search indexed documents by filename..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Documents Grid */}
      {filteredDocs.length === 0 ? (
        <div className="doc-list-empty" style={{ padding: '48px 24px' }}>
          <FileText size={40} style={{ opacity: 0.3, margin: '0 auto 12px auto' }} />
          <p style={{ fontSize: '1.05rem', fontWeight: 700 }}>No documents match your query</p>
          <p style={{ fontSize: '0.85rem', marginTop: '6px', color: 'var(--text-muted)' }}>
            {documents.length === 0
              ? 'Upload a PDF to populate your knowledge archive.'
              : 'Try searching for a different keyword.'}
          </p>
        </div>
      ) : (
        <div className="archive-grid">
          {filteredDocs.map((doc, idx) => {
            const colorVariant = COLOR_VARIANTS[idx % COLOR_VARIANTS.length];
            return (
              <div key={doc.source} className="archive-card">
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div className={`doc-icon ${colorVariant}`} style={{ width: '42px', height: '42px' }}>
                      <FileText size={22} />
                    </div>
                    <div>
                      <h4
                        style={{
                          fontSize: '0.98rem',
                          fontWeight: 700,
                          color: 'var(--text-primary)',
                          wordBreak: 'break-all',
                        }}
                      >
                        {doc.source}
                      </h4>
                      <span
                        style={{
                          fontSize: '0.78rem',
                          color: 'var(--text-muted)',
                          fontWeight: 600,
                        }}
                      >
                        PDF Document · {doc.chunk_count} chunk{doc.chunk_count !== 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>

                  <button
                    className="doc-delete-btn"
                    onClick={() => onRequestDelete(doc)}
                    disabled={deletingDoc === doc.source}
                    title="Delete document"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>

                <div
                  style={{
                    backgroundColor: 'var(--bg-surface-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '10px 14px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: '0.8rem',
                    color: 'var(--text-secondary)',
                  }}
                >
                  <span>Indexed in ChromaDB</span>
                  <span style={{ fontWeight: 700, color: 'var(--sage-green-text)' }}>● Active</span>
                </div>

                <button
                  className="btn-secondary"
                  onClick={() => onAskAboutDoc(doc)}
                  style={{
                    justifyContent: 'center',
                    gap: '8px',
                    padding: '10px 16px',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  <MessageSquare size={14} />
                  <span>Ask questions about this doc</span>
                  <ArrowRight size={13} style={{ marginLeft: 'auto' }} />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Direct Dropzone inside Archive */}
      <div
        className={`upload-dropzone ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        style={{ marginTop: '12px', padding: '36px 20px' }}
      >
        <div className="upload-icon-wrap">
          {isUploading ? <Loader2 size={24} className="spin-anim" /> : <UploadCloud size={24} />}
        </div>
        <div>
          <p className="upload-title">Drag and drop additional PDFs here to index</p>
          <p className="upload-subtitle">Files are split into overlapping chunks and embedded with Gemini</p>
        </div>
      </div>
    </div>
  );
}
