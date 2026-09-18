/**
 * API Service for communicating with the InquireAI FastAPI backend.
 */

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8000'
).replace(/\/+$/, '');

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    ...(options.headers || {}),
  };

  // If body is not FormData, default to JSON
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const isJson = response.headers.get('content-type')?.includes('application/json');
    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      let errorMessage = `HTTP Error ${response.status}`;
      if (typeof data === 'object' && data !== null) {
        if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail) && data.detail.length > 0) {
          errorMessage = data.detail.map((e) => e.msg || JSON.stringify(e)).join(', ');
        } else if (data.message) {
          errorMessage = data.message;
        }
      } else if (typeof data === 'string' && data.trim()) {
        errorMessage = data;
      }
      throw new ApiError(errorMessage, response.status, data);
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      `Network error: Unable to connect to InquireAI API at ${API_BASE_URL}. Ensure the backend server is running and accessible.`,
      0,
      null
    );
  }
}

export const api = {
  baseUrl: API_BASE_URL,

  /**
   * Health check
   */
  async checkHealth() {
    return request('/health');
  },

  /**
   * Get list of currently indexed documents
   */
  async getDocuments() {
    return request('/documents');
  },

  /**
   * Upload and index a PDF document
   * @param {File} file
   */
  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    return request('/upload', {
      method: 'POST',
      body: formData,
    });
  },

  /**
   * Query the knowledge base
   * @param {string} question
   * @param {number} topK
   */
  async sendQuery(question, topK = 5) {
    return request('/query', {
      method: 'POST',
      body: JSON.stringify({ question, top_k: Math.min(Math.max(1, topK), 5) }),
    });
  },

  /**
   * Delete an indexed document by filename
   * @param {string} filename
   */
  async deleteDocument(filename) {
    const encoded = encodeURIComponent(filename);
    return request(`/documents/${encoded}`, {
      method: 'DELETE',
    });
  },
};
