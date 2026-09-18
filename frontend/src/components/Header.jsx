import React from 'react';
import { Trash2, Menu, Upload, Sparkles } from 'lucide-react';

export default function Header({
  activeTab,
  hasMessages,
  onClearChat,
  onToggleSidebar,
  onToggleUpload,
}) {
  const getHeaderInfo = () => {
    switch (activeTab) {
      case 'chat':
        return {
          title: 'Chat with your knowledge base',
          subtitle: 'Ask questions grounded directly in your uploaded documents.',
        };
      case 'documents':
        return {
          title: 'Manage Documents',
          subtitle: 'View, index, and organize your PDF knowledge base.',
        };
      case 'settings':
        return {
          title: 'System Settings',
          subtitle: 'Configuration and connected RAG architecture details.',
        };
      case 'home':
      default:
        return {
          title: 'Knowledge Assistant Workspace',
          subtitle: 'Turn your documents into grounded, accurate answers.',
        };
    }
  };

  const { title, subtitle } = getHeaderInfo();

  return (
    <header className="workspace-header">
      <div className="header-title-wrap">
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <h1 className="header-title">{title}</h1>
          <span className="header-subtitle">{subtitle}</span>
        </div>
      </div>

      <div className="header-actions">
        {/* Clear chat button */}
        {hasMessages && (
          <button
            className="btn-secondary"
            onClick={onClearChat}
            title="Clear current conversation"
          >
            <Trash2 size={14} />
            <span>Clear chat</span>
          </button>
        )}

        {/* Mobile / tablet drawer toggles */}
        <button
          className="btn-icon mobile-only"
          onClick={onToggleUpload}
          title="Toggle upload panel"
          style={{ display: 'none' }}
        >
          <Upload size={18} />
        </button>
      </div>
    </header>
  );
}
