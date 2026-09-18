/**
 * API Service for communicating with the KnoBase FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

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
      const errorMessage =
        (typeof data === 'object' && data?.detail) ||
        (typeof data === 'string' && data) ||
        `HTTP Error ${response.status}`;
      throw new ApiError(errorMessage, response.status, data);
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      `Network error: Unable to connect to KnoBase API at ${API_BASE_URL}. Ensure the backend server is running.`,
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
    return request('/');
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
   */
  async sendQuery(question) {
    return request('/query', {
      method: 'POST',
      body: JSON.stringify({ question }),
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
