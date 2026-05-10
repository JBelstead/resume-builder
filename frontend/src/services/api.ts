import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

// Profile
export const profileApi = {
  get: () => api.get('/profile'),
  upsert: (data: object) => api.put('/profile', data),
}

// Education
export const educationApi = {
  list: () => api.get('/education'),
  create: (data: object) => api.post('/education', data),
  update: (id: number, data: object) => api.put(`/education/${id}`, data),
  remove: (id: number) => api.delete(`/education/${id}`),
}

// Certifications
export const certificationsApi = {
  list: () => api.get('/certifications'),
  create: (data: object) => api.post('/certifications', data),
  update: (id: number, data: object) => api.put(`/certifications/${id}`, data),
  remove: (id: number) => api.delete(`/certifications/${id}`),
}

// Experience
export const experienceApi = {
  list: () => api.get('/experience'),
  create: (data: object) => api.post('/experience', data),
  update: (id: number, data: object) => api.put(`/experience/${id}`, data),
  remove: (id: number) => api.delete(`/experience/${id}`),
}

// Resume
export const resumeApi = {
  generate: (data: object) => api.post('/resume/generate', data),
  list: () => api.get('/resume'),
  get: (id: number) => api.get(`/resume/${id}`),
  downloadUrl: (id: number) => `http://localhost:8000/api/resume/${id}/download`,
  remove: (id: number) => api.delete(`/resume/${id}`),
}

export default api
