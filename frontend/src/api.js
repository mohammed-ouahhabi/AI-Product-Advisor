import axios from 'axios'

const token = () => localStorage.getItem('auth_token')

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
})

api.interceptors.request.use((config) => {
  const authToken = token()
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`
  }
  return config
})
