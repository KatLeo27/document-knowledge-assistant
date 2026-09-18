import React from 'react';
import {
  Home,
  MessageSquare,
  FileText,
  Settings,
  Sparkles,
  Database,
  Layers,
  RefreshCw,
} from 'lucide-react';
import logoImg from '../assets/logo.png';

export default function Sidebar({
  activeTab,
  setActiveTab,
  stats,
  isRefreshingStats,
  onRefreshStats,
  backendConnected,
}) {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand" onClick={() => setActiveTab('home')} title="InquireAI Home">
        <img
          src={logoImg}
          alt="InquireAI Logo"
          className="brand-logo-img"
        />
        <span className="brand-name">InquireAI</span>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon className="nav-icon" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Knowledge Base Statistics Section */}
      <div className="sidebar-stats-section">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span className="stats-title">My Knowledge Base</span>
          <button
            className="btn-icon"
            onClick={onRefreshStats}
            title="Refresh statistics"
            disabled={isRefreshingStats}
            style={{ opacity: isRefreshingStats ? 0.5 : 1 }}
          >
            <RefreshCw size={13} className={isRefreshingStats ? 'spin-anim' : ''} />
          </button>
        </div>

        <div className="stats-card-group">
          {/* Documents Card (Pastel Sage) */}
          <div className="stat-card sage">
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <FileText size={14} />
              <span className="stat-label">Documents</span>
            </div>
            <span className="stat-value">{stats.documentCount}</span>
          </div>

          {/* Chunks Card (Pastel Rose) */}
          <div className="stat-card rose">
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Layers size={14} />
              <span className="stat-label">Total Chunks</span>
            </div>
            <span className="stat-value">{stats.chunkCount}</span>
          </div>
        </div>

        {/* Vector Store Connection Status Pill */}
        <div className="status-pill">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={15} style={{ color: 'var(--text-muted)' }} />
            <span>Vector Store</span>
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
            <span>{backendConnected ? 'Connected' : 'Offline'}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
