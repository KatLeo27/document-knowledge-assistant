import React from 'react';
import { FileText, Trash2 } from 'lucide-react';

const COLOR_VARIANTS = ['pink', 'blue', 'yellow', 'sage'];

export default function DocumentCard({ doc, index, onRequestDelete, isDeleting }) {
  const colorVariant = COLOR_VARIANTS[index % COLOR_VARIANTS.length];

  return (
    <div className="doc-card">
      <div className="doc-info-wrap">
        <div className={`doc-icon ${colorVariant}`}>
          <FileText size={18} />
        </div>
        <div className="doc-details">
          <span className="doc-filename" title={doc.source}>
            {doc.source}
          </span>
          <span className="doc-meta">
            {doc.chunk_count} chunk{doc.chunk_count !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      <button
        className="doc-delete-btn"
        onClick={() => onRequestDelete(doc)}
        disabled={isDeleting}
        title={`Delete ${doc.source}`}
      >
        <Trash2 size={16} />
      </button>
    </div>
  );
}
