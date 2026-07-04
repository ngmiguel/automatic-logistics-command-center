import axios from 'axios';
import { useAuthStore } from '@/store/authStore';

const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  },
);

export const getWsUrl = (path: string) => {
  const base =
    process.env.EXPO_PUBLIC_WS_URL ||
    API_BASE.replace(/^http/, 'ws');
  return `${base}${path}`;
};
