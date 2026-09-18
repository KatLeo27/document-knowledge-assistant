import React, { useRef, useEffect } from 'react';
import {
  HelpCircle,
  Files,
  ShieldCheck,
  Zap,
  Sparkles,
} from 'lucide-react';
import FeatureCard from './FeatureCard';
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
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoadingQuery]);

  const hasMessages = messages.length > 0;

  return (
    <main className="main-workspace">
      <div className="chat-messages-container">
        {!hasMessages ? (
          /* Empty / Welcome Hero State */
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

            {/* 4 Feature Cards */}
            <div className="features-grid">
              <FeatureCard
                icon={HelpCircle}
                color="green"
                title="Ask Questions"
                description="Get answers directly extracted and synthesized from your documents."
              />
              <FeatureCard
                icon={Files}
                color="pink"
                title="Multiple Documents"
                description="Work with all your indexed PDFs seamlessly in a unified knowledge base."
              />
              <FeatureCard
                icon={ShieldCheck}
                color="yellow"
                title="Grounded Answers"
                description="See exact page citations and stay confident against hallucinations."
              />
              <FeatureCard
                icon={Zap}
                color="blue"
                title="Save Time"
                description="Find key information, summaries, and definitions in seconds."
              />
            </div>

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

            <div ref={messagesEndRef} />
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
