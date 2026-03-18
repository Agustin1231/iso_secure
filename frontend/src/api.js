import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
});

export const dashboardApi = {
  getSummary: () => api.get('/dashboard/summary').then(res => res.data),
  getKpis: () => api.get('/dashboard/kpis').then(res => res.data),
  getExport: () => api.get('/dashboard/export').then(res => res.data),
};

export const incidentApi = {
  getAll: (params) => api.get('/incidents', { params }).then(res => res.data),
  getStats: (days) => api.get('/incidents/stats', { params: { days } }).then(res => res.data),
  create: (data) => api.post('/incidents', data).then(res => res.data),
};

export const riskApi = {
  getCurrent: () => api.get('/risk/current').then(res => res.data),
  getByDomain: () => api.get('/risk/by-domain').then(res => res.data),
  getHistory: (params) => api.get('/risk/history', { params }).then(res => res.data),
};

export const controlApi = {
  getAll: (params) => api.get('/controls', { params }).then(res => res.data),
  getCompliance: () => api.get('/controls/compliance').then(res => res.data),
};

export const snapshotApi = {
  getHistory: (limit) => api.get('/snapshots', { params: { limit } }).then(res => res.data),
  create: () => api.post('/snapshots').then(res => res.data),
};

export default api;
