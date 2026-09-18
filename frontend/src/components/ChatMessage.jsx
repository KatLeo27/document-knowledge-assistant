import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Sparkles, CheckCircle2, AlertCircle, ChevronDown, ChevronUp, Layers } from 'lucide-react';
import SourceCard from './SourceCard';

export default function ChatMessage({ message }) {
  const [showDetails, setShowDetails] = useState(false);
  const isUser = message.sender === 'user';

  if (isUser) {
    return (
      <div className="message-row user">
        <div className="user-bubble">
          {message.text}
        </div>
      </div>
    );
  }

  const isGrounded =
    message.isGrounded !== undefined
      ? message.isGrounded
      : Boolean(message.sources && message.sources.length > 0 && !message.text.toLowerCase().includes('not contain information') && !message.text.toLowerCase().includes('not found'));

  return (
    <div className="message-row assistant">
      <div className="assistant-card">
        {/* Assistant Header with Grounded Badge */}
        <div className="assistant-header">
          <div className="assistant-identity">
            <div className="assistant-avatar">
              <Sparkles size={14} />
            </div>
            <span className="assistant-name">InquireAI Assistant</span>
          </div>

          {/* Grounded Indicator Badge */}
          {isGrounded ? (
            <span className="grounded-badge grounded" title="Response is strictly derived from your document excerpts">
              <CheckCircle2 size={12} />
              <span>Grounded in your documents</span>
            </span>
          ) : (
            <span className="grounded-badge ungrounded" title="Document excerpts did not contain sufficient information">
              <AlertCircle size={12} />
              <span>Not found in your knowledge base</span>
            </span>
          )}
        </div>

        {/* Answer Content with Markdown */}
        <div className="markdown-body">
          <ReactMarkdown>{message.text}</ReactMarkdown>
        </div>

        {/* Sources Section */}
        {message.sources && message.sources.length > 0 && (
          <div className="sources-section">
            <span className="sources-header">Sources & Citations</span>
            <div className="sources-grid">
              {/* Deduplicate source & page */}
              {Array.from(
                new Map(
                  message.sources.map((src) => [`${src.source}_${src.page_number}`, src])
                ).values()
              ).map((src, idx) => (
                <SourceCard
                  key={idx}
                  source={src.source}
                  pageNumber={src.page_number}
                  chunkId={src.chunk_id}
                />
              ))}
            </div>

            {/* Optional Expandable Retrieval Details */}
            {message.sources.length > 0 && (
              <div style={{ marginTop: '6px' }}>
                <button
                  className="retrieval-details-toggle"
                  onClick={() => setShowDetails(!showDetails)}
                >
                  <Layers size={13} />
                  <span>{showDetails ? 'Hide retrieval details' : 'View retrieval details'}</span>
                  {showDetails ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                </button>

                {showDetails && (
                  <div className="retrieval-details-box">
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                      Retrieved {message.sources.length} chunk{message.sources.length > 1 ? 's' : ''}:
                    </span>
                    {message.sources.map((src, i) => (
                      <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                        <span>
                          <strong>{src.source}</strong> · Page {src.page_number}
                        </span>
                        {src.chunk_id && (
                          <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                            {src.chunk_id}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
