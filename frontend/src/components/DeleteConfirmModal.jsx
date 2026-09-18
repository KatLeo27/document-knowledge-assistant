import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function DeleteConfirmModal({ doc, onConfirm, onCancel, isDeleting }) {
  if (!doc) return null;

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--pink-100)',
              color: 'var(--pink-600)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <AlertTriangle size={20} />
          </div>
          <h3 className="modal-title">Delete Document</h3>
        </div>

        <p className="modal-desc">
          Are you sure you want to delete <strong>{doc.source}</strong>?
          <br />
          This will remove all <strong>{doc.chunk_count}</strong> indexed vector chunks from your ChromaDB knowledge base.
        </p>

        <div className="modal-actions">
          <button className="btn-secondary" onClick={onCancel} disabled={isDeleting}>
            Cancel
          </button>
          <button className="btn-danger" onClick={onConfirm} disabled={isDeleting}>
            {isDeleting ? 'Deleting...' : 'Delete Document'}
          </button>
        </div>
      </div>
    </div>
  );
}
