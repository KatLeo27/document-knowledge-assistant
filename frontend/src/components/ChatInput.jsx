import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Sparkles, Loader2 } from 'lucide-react';

export default function ChatInput({ onSendMessage, isLoading, placeholder }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    onSendMessage(trimmed);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="chat-input-wrapper">
      <form className="chat-input-box" onSubmit={handleSubmit}>
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          rows={1}
          placeholder={placeholder || 'Ask a question about your documents...'}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />

        <button
          type="submit"
          className="send-btn"
          disabled={!input.trim() || isLoading}
          title={isLoading ? 'Generating grounded answer...' : 'Send question (Enter)'}
        >
          {isLoading ? (
            <Loader2 size={18} className="spin-anim" />
          ) : (
            <ArrowUp size={18} />
          )}
        </button>
      </form>
    </div>
  );
}
