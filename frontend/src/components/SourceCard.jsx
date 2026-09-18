import React from 'react';
import { FileText } from 'lucide-react';

export default function SourceCard({ source, pageNumber, chunkId }) {
  return (
    <div className="source-card" title={chunkId ? `Chunk: ${chunkId}` : undefined}>
      <FileText size={14} className="source-icon" />
      <span className="source-name">{source}</span>
      <span className="source-page">Page {pageNumber}</span>
    </div>
  );
}
