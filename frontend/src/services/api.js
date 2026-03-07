import axios from 'axios';

// API_BASE_URL: dùng REACT_APP_API_URL nếu được cấu hình (Render/production), 
// fallback về localhost khi chạy dev.
// const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://psychology-support-chatbot.onrender.com';
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {'Content-Type': 'application/json'},
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export { API_BASE_URL };
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  getMe: () => api.get('/api/auth/me'),
};

export const chatAPI = {
  createSession: (data) => api.post('/api/chat/sessions', data),
  getSessions: () => api.get('/api/chat/sessions'),
  getSession: (sessionId) => api.get(`/api/chat/sessions/${sessionId}`),
  sendMessage: (sessionId, message) => api.post(`/api/chat/sessions/${sessionId}/messages`, message),
  deleteSession: (sessionId) => api.delete(`/api/chat/sessions/${sessionId}`),
  getMessageCount: () => api.get('/api/chat/message-count'),
  submitRating: (ratingData) => api.post('/api/chat/rating', ratingData),
};

export const teacherAPI = {
  getAllStudentsHistory: () => api.get('/api/teacher/students'),
  getStudentSessions: (studentId) => api.get(`/api/teacher/students/${studentId}/sessions`),
  getSessionDetails: (sessionId) => api.get(`/api/teacher/sessions/${sessionId}`),
};

export const documentAPI = {
  upload: (formData) => api.post('/api/documents/upload', formData, {
    headers: {'Content-Type': 'multipart/form-data'},
  }),
  getDocuments: () => api.get('/api/documents'),
};

export default api;
