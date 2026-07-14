import axios from 'axios';

// Configure Axios instance for backend connectivity
export const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getSystemStatus = async () => {
  const res = await api.get('/system/status');
  return res.data;
};

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export const processDocument = async (documentId) => {
  const res = await api.post(`/documents/${documentId}/process`);
  return res.data;
};

export const embedDocument = async (documentId) => {
  const res = await api.post(`/documents/${documentId}/embed`);
  return res.data;
};

export const buildGraph = async (documentId) => {
  const res = await api.post(`/graph/build/${documentId}`);
  return res.data;
};

export const chatWithAgents = async (question, conversationId) => {
  const res = await api.post('/chat/', {
    question,
    conversation_id: conversationId,
  });
  return res.data;
};

export const semanticSearch = async (query, topK = 5, threshold = 0.3) => {
  const res = await api.post('/search/', {
    query,
    top_k: topK,
    threshold
  });
  return res.data;
};

export const getGraphQuery = async (query) => {
  // Using an abstract endpoint for the UI visualizer
  const res = await api.post('/graph/query', { query });
  return res.data;
};
