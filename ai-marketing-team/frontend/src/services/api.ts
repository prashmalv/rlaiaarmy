import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const runApi = {
  triggerDaily: (data: { day_focus?: string; posting_mode?: string }) =>
    api.post('/run/daily', data).then(r => r.data),
  getRun: (id: string) => api.get(`/run/${id}`).then(r => r.data),
}

export const leadsApi = {
  getAll: () => api.get('/leads').then(r => r.data.leads),
  create: (data: any) => api.post('/leads', data).then(r => r.data),
  delete: (id: string) => api.delete(`/leads/${id}`).then(r => r.data),
}

export const postsApi = {
  getAll: () => api.get('/posts').then(r => r.data.posts),
  approve: (id: string) => api.post(`/posts/${id}/approve`).then(r => r.data),
  publish: (id: string) => api.post(`/posts/${id}/publish`).then(r => r.data),
}

export const opportunitiesApi = {
  getAll: () => api.get('/opportunities').then(r => r.data.opportunities),
  updateStatus: (id: string, status: string) =>
    api.patch(`/opportunities/${id}/status`, { status }).then(r => r.data),
}

export const generateApi = {
  content: (data: any) => api.post('/generate/content', data).then(r => r.data),
  email: (leadId: string, type = 'nurture') =>
    api.post(`/generate/email?lead_id=${leadId}&email_type=${type}`).then(r => r.data),
  weeklyCalendar: (focus?: string) =>
    api.get('/generate/weekly-calendar', { params: { focus } }).then(r => r.data),
  leadSuggestions: () => api.get('/generate/lead-suggestions').then(r => r.data),
}

export const statsApi = {
  get: () => api.get('/stats').then(r => r.data),
}
