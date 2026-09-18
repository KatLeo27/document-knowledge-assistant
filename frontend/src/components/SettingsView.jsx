import React from 'react';
import {
  Moon,
  Sun,
  Sliders,
  Database,
  Cpu,
  Server,
  Trash2,
  RefreshCw,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Layers,
} from 'lucide-react';

export default function SettingsView({
  theme,
  onToggleTheme,
  topK,
  onChangeTopK,
  stats,
  backendConnected,
  onClearChat,
  onRefreshStats,
  isRefreshingStats,
  hasMessages,
}) {
  return (
    <div className="settings-view">
      {/* Header Banner */}
      <div className="archive-header-card">
        <div>
          <div className="hero-badge" style={{ marginBottom: '10px' }}>
            <Sparkles size={14} />
            <span>Preferences & System</span>
          </div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            Settings & Architecture
          </h2>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Customize your visual theme, tune RAG retrieval parameters, and monitor system health.
          </p>
        </div>
      </div>

      {/* Appearance Section */}
      <div className="settings-section-card">
        <h3 className="settings-section-title">
          <Sun size={18} style={{ color: 'var(--warm-butter-text)' }} />
          <span>Appearance & Theme</span>
        </h3>

        <div className="settings-row">
          <div className="settings-label-wrap">
            <span className="settings-label">Interface Theme</span>
            <span className="settings-desc">
              Toggle between warm parchment Light mode and obsidian Dark mode.
            </span>
          </div>

          <button
            className="theme-toggle-btn"
            onClick={onToggleTheme}
            style={{
              backgroundColor: theme === 'dark' ? 'var(--lavender-light)' : 'var(--warm-butter-light)',
              borderColor: theme === 'dark' ? 'var(--lavender-border)' : 'var(--warm-butter-border)',
              color: theme === 'dark' ? 'var(--lavender-text)' : 'var(--warm-butter-text)',
            }}
          >
            {theme === 'dark' ? (
              <>
                <Moon size={16} />
                <span>Dark Mode (Active)</span>
              </>
            ) : (
              <>
                <Sun size={16} />
                <span>Light Mode (Active)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* RAG Retrieval Parameters */}
      <div className="settings-section-card">
        <h3 className="settings-section-title">
          <Sliders size={18} style={{ color: 'var(--sage-green-text)' }} />
          <span>RAG Retrieval Tuning</span>
        </h3>

        <div className="settings-row">
          <div className="settings-label-wrap">
            <span className="settings-label">Top-K Retrieval Depth</span>
            <span className="settings-desc">
              Number of most relevant vector chunks retrieved from ChromaDB for answering queries (Current: {topK}).
            </span>
          </div>

          <div className="slider-control">
            <input
              type="range"
              min="1"
              max="10"
              step="1"
              value={topK}
              onChange={(e) => onChangeTopK(Number(e.target.value))}
              style={{ width: '130px' }}
            />
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontWeight: 700,
                fontSize: '1rem',
                minWidth: '24px',
                textAlign: 'center',
                color: 'var(--sage-green-text)',
              }}
            >
              {topK}
            </span>
          </div>
        </div>
      </div>

      {/* System & Architecture Status */}
      <div className="settings-section-card">
        <h3 className="settings-section-title">
          <Server size={18} style={{ color: 'var(--lavender-text)' }} />
          <span>Architecture & Model Pipeline</span>
        </h3>

        <div className="settings-row">
          <div className="settings-label-wrap">
            <span className="settings-label">FastAPI Backend Server</span>
            <span className="settings-desc">REST API entry point at http://127.0.0.1:8000</span>
          </div>
          <div className="status-indicator">
            <span
              className="status-dot"
              style={{
                backgroundColor: backendConnected ? '#3bb35c' : '#e05353',
                boxShadow: backendConnected
                  ? '0 0 0 3px rgba(59, 179, 92, 0.2)'
                  : '0 0 0 3px rgba(224, 83, 83, 0.2)',
              }}
            />
            <span style={{ fontWeight: 700 }}>{backendConnected ? 'Connected & Healthy' : 'Offline'}</span>
          </div>
        </div>

        <div className="settings-row">
          <div className="settings-label-wrap">
            <span className="settings-label">Vector Store</span>
            <span className="settings-desc">ChromaDB persistent collection (`document_knowledge`)</span>
          </div>
          <span
            style={{
              fontSize: '0.82rem',
              fontWeight: 700,
              padding: '4px 10px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--sage-green-light)',
              color: 'var(--sage-green-text)',
              border: '1px solid var(--sage-green-border)',
            }}
          >
            {stats.documentCount} Docs · {stats.chunkCount} Chunks
          </span>
        </div>

        <div className="settings-row">
          <div className="settings-label-wrap">
            <span className="settings-label">Embedding Model</span>
            <span className="settings-desc">Google Gemini text embeddings</span>
          </div>
          <code
            style={{
              fontSize: '0.8rem',
              fontWeight: 600,
              padding: '4px 8px',
              borderRadius: 'var(--radius-xs)',
              backgroundColor: 'var(--bg-surface-subtle)',
              border: '1px solid var(--border-light)',
              color: 'var(--text-secondary)',
            }}
          >
            gemini-embedding-001 (768-dim)
          </code>
        </div>

        <div className="settings-row">
          <div className="settings-label-wrap">
            <span className="settings-label">Generator LLM</span>
            <span className="settings-desc">Google Gemini multimodal generative foundation model</span>
          </div>
          <code
            style={{
              fontSize: '0.8rem',
              fontWeight: 600,
              padding: '4px 8px',
              borderRadius: 'var(--radius-xs)',
              backgroundColor: 'var(--bg-surface-subtle)',
              border: '1px solid var(--border-light)',
              color: 'var(--text-secondary)',
            }}
          >
            gemini-2.5-flash
          </code>
        </div>
      </div>

      {/* Data Management Actions */}
      <div className="settings-section-card">
        <h3 className="settings-section-title">
          <ShieldCheck size={18} style={{ color: 'var(--blush-rose-text)' }} />
          <span>Data Actions</span>
        </h3>

        <div className="settings-row">
          <div className="settings-label-wrap">
            <span className="settings-label">Clear Conversation History</span>
            <span className="settings-desc">
              Reset the active chat messages and citation history in memory.
            </span>
          </div>
          <button
            className="btn-secondary"
            onClick={onClearChat}
            disabled={!hasMessages}
            style={{ opacity: hasMessages ? 1 : 0.5 }}
          >
            <Trash2 size={15} style={{ color: 'var(--blush-rose-text)' }} />
            <span>Clear Chat</span>
          </button>
        </div>

        <div className="settings-row">
          <div className="settings-label-wrap">
            <span className="settings-label">Re-sync Vector Store Statistics</span>
            <span className="settings-desc">
              Fetch the latest document and chunk counts from the ChromaDB collection.
            </span>
          </div>
          <button
            className="btn-secondary"
            onClick={onRefreshStats}
            disabled={isRefreshingStats}
          >
            <RefreshCw size={14} className={isRefreshingStats ? 'spin-anim' : ''} />
            <span>Re-sync Stats</span>
          </button>
        </div>
      </div>
    </div>
  );
}
