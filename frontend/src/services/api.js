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

export const getSystemMetrics = async () => {
  const res = await api.get('/system/metrics');
  return res.data;
};

export const getSystemLogs = async (lines = 100) => {
  const res = await api.get(`/system/logs?lines=${lines}`);
  return res.data;
};

export const getSystemRoutes = async () => {
  const res = await api.get('/system/routes');
  return res.data;
};

export const deleteDocument = async (documentId) => {
  const res = await api.delete(`/documents/${documentId}`);
  return res.data;
};

export const getDocumentText = async (documentId) => {
  const res = await api.get(`/documents/${documentId}/text`);
  return res.data;
};

export const getDocumentDetails = async (documentId) => {
  const res = await api.get(`/documents/${documentId}`);
  return res.data;
};

export const downloadOriginalPDF = (documentId) => {
  return `${api.defaults.baseURL}/documents/${documentId}/download`;
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

export const getProcessedDocuments = async () => {
  const res = await api.get('/documents/');
  return res.data;
};
