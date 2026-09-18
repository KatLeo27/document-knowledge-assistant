import React, { useRef, useEffect } from 'react';
import { Sparkles } from 'lucide-react';
import SuggestedQuestions from './SuggestedQuestions';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

export default function ChatWorkspace({
  messages,
  isLoadingQuery,
  onSendMessage,
  onSelectSuggestion,
  documentCount,
}) {
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages, isLoadingQuery]);

  const hasMessages = messages.length > 0;

  return (
    <main className="main-workspace">
      <div className="chat-messages-container" ref={chatContainerRef}>
        {!hasMessages ? (
          /* Clean & Minimal Welcome Hero State */
          <div className="empty-workspace">
            <div className="hero-badge">
              <Sparkles size={14} />
              <span>Multi-Document Knowledge Intelligence</span>
            </div>

            <h2 className="hero-heading">
              Turn your documents <br />
              <span>into answers.</span>
            </h2>

            <p className="hero-subtext">
              Upload your documents, ask questions, and get accurate, grounded answers using AI.
            </p>

            {/* Suggested Question Pills */}
            <SuggestedQuestions onSelectQuestion={onSelectSuggestion} />
          </div>
        ) : (
          /* Active Chat Stream */
          <>
            {messages.map((msg, index) => (
              <ChatMessage key={index} message={msg} />
            ))}

            {/* Loading Indicator Card */}
            {isLoadingQuery && (
              <div className="message-row assistant">
                <div className="assistant-card" style={{ padding: '16px 20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div className="assistant-avatar">
                      <Sparkles size={14} />
                    </div>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                      Searching knowledge base and generating grounded answer...
                    </span>
                    <div className="typing-indicator">
                      <span className="typing-dot" />
                      <span className="typing-dot" />
                      <span className="typing-dot" />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Persistent Chat Input */}
      <ChatInput
        onSendMessage={onSendMessage}
        isLoading={isLoadingQuery}
        placeholder={
          hasMessages
            ? 'Ask a follow-up question...'
            : documentCount > 0
            ? 'Ask anything about your indexed documents...'
            : 'Upload a PDF to start asking questions...'
        }
      />
    </main>
  );
}
