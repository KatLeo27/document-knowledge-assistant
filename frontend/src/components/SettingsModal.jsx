import React from 'react';
import { Settings, Server, Cpu, Database, X, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export default function SettingsModal({ isOpen, onClose, backendConnected }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--sage-100)',
                color: 'var(--sage-700)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Settings size={18} />
            </div>
            <h3 className="modal-title">System & Architecture</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' }}>
          {/* Backend API */}
          <div className="doc-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Server size={18} style={{ color: 'var(--sage-600)' }} />
              <div>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Backend API Base URL
                </span>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{api.baseUrl}</p>
              </div>
            </div>
            <span className="grounded-badge grounded">
              {backendConnected ? 'Active' : 'Offline'}
            </span>
          </div>

          {/* Embedding Model */}
          <div className="doc-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Cpu size={18} style={{ color: 'var(--blue-600)' }} />
              <div>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Embedding Model
                </span>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  gemini-embedding-001 (768 dimensions)
                </p>
              </div>
            </div>
            <span className="grounded-badge grounded">Active</span>
          </div>

          {/* Generative LLM */}
          <div className="doc-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Cpu size={18} style={{ color: 'var(--pink-600)' }} />
              <div>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Generative LLM
                </span>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  gemini-2.5-flash (temperature: 0.0)
                </p>
              </div>
            </div>
            <span className="grounded-badge grounded">Active</span>
          </div>

          {/* Vector Store */}
          <div className="doc-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Database size={18} style={{ color: 'var(--yellow-600)' }} />
              <div>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Vector Store
                </span>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Persistent ChromaDB (collection: document_knowledge)
                </p>
              </div>
            </div>
            <span className="grounded-badge grounded">Active</span>
          </div>
        </div>

        <div className="modal-actions" style={{ marginTop: '12px' }}>
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
