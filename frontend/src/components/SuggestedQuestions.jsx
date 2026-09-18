import React from 'react';
import { HelpCircle, Sparkles } from 'lucide-react';

const DEFAULT_SUGGESTIONS = [
  'What are the problems with traditional approach for storing data?',
  'What is Database according to the document?',
  'Explain ACID properties.',
  'What is a transaction in DBMS?',
];

export default function SuggestedQuestions({ onSelectQuestion, customSuggestions }) {
  const suggestions = customSuggestions || DEFAULT_SUGGESTIONS;

  return (
    <div className="suggestions-section">
      <span className="suggestions-label">Try asking a question</span>
      <div className="suggestions-list">
        {suggestions.map((q, idx) => (
          <button
            key={idx}
            className="suggestion-pill"
            onClick={() => onSelectQuestion(q)}
          >
            <Sparkles size={13} style={{ color: 'var(--sage-600)' }} />
            <span>{q}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
