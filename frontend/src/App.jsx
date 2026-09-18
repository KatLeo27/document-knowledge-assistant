import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatWorkspace from './components/ChatWorkspace';
import UploadPanel from './components/UploadPanel';
import DocumentArchiveView from './components/DocumentArchiveView';
import SettingsView from './components/SettingsView';
import Toast from './components/Toast';
import DeleteConfirmModal from './components/DeleteConfirmModal';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState({ documentCount: 0, chunkCount: 0 });
  const [isRefreshingStats, setIsRefreshingStats] = useState(false);
  const [backendConnected, setBackendConnected] = useState(true);

  // Theme state ('light' | 'dark')
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('inquireai_theme') || 'light';
  });

  // Top-K retrieval parameter
  const [topK, setTopK] = useState(() => {
    const saved = localStorage.getItem('inquireai_top_k');
    return saved ? Number(saved) : 5;
  });

  const [messages, setMessages] = useState([]);
  const [isLoadingQuery, setIsLoadingQuery] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const [docToDelete, setDocToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [toasts, setToasts] = useState([]);

  // Apply theme to root document element & persist
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('inquireai_theme', theme);
  }, [theme]);

  // Persist top-K
  useEffect(() => {
    localStorage.setItem('inquireai_top_k', topK.toString());
  }, [topK]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Add toast notification
  const addToast = useCallback((message, type = 'success', duration = 4500) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const dismissToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Fetch documents and compute knowledge base stats
  const fetchDocuments = useCallback(async () => {
    setIsRefreshingStats(true);
    try {
      const data = await api.getDocuments();
      const docList = data.documents || [];
      setDocuments(docList);

      const totalChunks = docList.reduce((acc, doc) => acc + (doc.chunk_count || 0), 0);
      setStats({
        documentCount: docList.length,
        chunkCount: totalChunks,
      });
      setBackendConnected(true);
    } catch (error) {
      setBackendConnected(false);
      addToast(error.message, 'error');
    } finally {
      setIsRefreshingStats(false);
    }
  }, [addToast]);

  // Initial load
  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Send a RAG query
  const handleSendMessage = async (question) => {
    if (!question.trim() || isLoadingQuery) return;

    // Switch to chat workspace view if on Home or other tabs
    if (activeTab !== 'chat') {
      setActiveTab('chat');
    }

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoadingQuery(true);

    try {
      const response = await api.sendQuery(question);

      const isUngrounded =
        !response.sources ||
        response.sources.length === 0 ||
        response.answer.toLowerCase().includes('not contain information') ||
        response.answer.toLowerCase().includes('not found') ||
        response.answer.toLowerCase().includes("couldn't find");

      const assistantMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: response.answer,
        sources: response.sources || [],
        isGrounded: !isUngrounded,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: `**Query Error:** ${error.message}`,
        sources: [],
        isGrounded: false,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      addToast(error.message, 'error');
    } finally {
      setIsLoadingQuery(false);
    }
  };

  // Upload and index a PDF file
  const handleUploadFile = async (file) => {
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      addToast('Invalid file format. Only PDF files are supported.', 'error');
      return;
    }

    setIsUploading(true);
    try {
      const result = await api.uploadDocument(file);
      addToast(
        `Successfully indexed "${result.source}" (${result.chunks_added} chunks added)`,
        'success'
      );
      await fetchDocuments();
    } catch (error) {
      addToast(`Upload failed: ${error.message}`, 'error');
    } finally {
      setIsUploading(false);
    }
  };

  // Delete document
  const handleConfirmDelete = async () => {
    if (!docToDelete) return;

    setIsDeleting(true);
    try {
      const result = await api.deleteDocument(docToDelete.source);
      addToast(
        `Deleted "${result.source}" (${result.chunks_deleted} chunks removed)`,
        'info'
      );
      setDocToDelete(null);
      await fetchDocuments();
    } catch (error) {
      addToast(`Delete failed: ${error.message}`, 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  // Clear chat
  const handleClearChat = () => {
    if (messages.length === 0) return;
    setMessages([]);
    addToast('Conversation cleared.', 'info');
  };

  // Ask about a specific document from Archive
  const handleAskAboutDoc = (doc) => {
    setActiveTab('chat');
    handleSendMessage(`What are the key concepts and topics covered in ${doc.source}?`);
  };

  const showRightPanel = activeTab === 'home' || activeTab === 'chat';

  return (
    <div className="app-container">
      {/* Pastel Background Blobs */}
      <div className="pastel-blob blob-1" />
      <div className="pastel-blob blob-2" />
      <div className="pastel-blob blob-3" />
      <div className="pastel-blob blob-4" />

      {/* Left Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        stats={stats}
        isRefreshingStats={isRefreshingStats}
        onRefreshStats={fetchDocuments}
        backendConnected={backendConnected}
      />

      {/* Main Column */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0, overflow: 'hidden' }}>
        <Header
          activeTab={activeTab}
          hasMessages={messages.length > 0}
          onClearChat={handleClearChat}
        />

        {activeTab === 'home' || activeTab === 'chat' ? (
          <ChatWorkspace
            messages={messages}
            isLoadingQuery={isLoadingQuery}
            onSendMessage={handleSendMessage}
            onSelectSuggestion={handleSendMessage}
            documentCount={documents.length}
          />
        ) : activeTab === 'documents' ? (
          <DocumentArchiveView
            documents={documents}
            isUploading={isUploading}
            onUploadFile={handleUploadFile}
            onRequestDelete={(doc) => setDocToDelete(doc)}
            deletingDoc={docToDelete?.source}
            onAskAboutDoc={handleAskAboutDoc}
          />
        ) : activeTab === 'settings' ? (
          <SettingsView
            theme={theme}
            onToggleTheme={toggleTheme}
            topK={topK}
            onChangeTopK={setTopK}
            stats={stats}
            backendConnected={backendConnected}
            onClearChat={handleClearChat}
            onRefreshStats={fetchDocuments}
            isRefreshingStats={isRefreshingStats}
            hasMessages={messages.length > 0}
          />
        ) : null}
      </div>

      {/* Right Panel (Upload & Quick Document Management on Home & Chat) */}
      {showRightPanel && (
        <UploadPanel
          documents={documents}
          isUploading={isUploading}
          onUploadFile={handleUploadFile}
          onRequestDelete={(doc) => setDocToDelete(doc)}
          deletingDoc={docToDelete?.source}
        />
      )}

      {/* Modals & Toasts */}
      <DeleteConfirmModal
        doc={docToDelete}
        onConfirm={handleConfirmDelete}
        onCancel={() => setDocToDelete(null)}
        isDeleting={isDeleting}
      />

      <Toast toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}
