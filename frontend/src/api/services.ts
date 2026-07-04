import { apiClient } from './client';
import type { DashboardSummary, Incident, Mission, Notification, User, Vehicle, VirtualDriver, Telemetry } from '@/types';

export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post<{ access_token: string; role: string; user_id: string }>('/auth/login', { email, password }),
  register: (data: { email: string; password: string; full_name: string; role: string }) =>
    apiClient.post<User>('/auth/register', data),
  me: () => apiClient.get<User>('/auth/me'),
};

export const fleetApi = {
  listVehicles: (params?: { state?: string; limit?: number }) =>
    apiClient.get<Vehicle[]>('/fleet/vehicles', { params }),
  getVehicle: (id: string) => apiClient.get<Vehicle>(`/fleet/vehicles/${id}`),
  createVehicle: (data: Partial<Vehicle>) => apiClient.post<Vehicle>('/fleet/vehicles', data),
  listDrivers: (availableOnly = false) =>
    apiClient.get<VirtualDriver[]>('/fleet/drivers', { params: { available_only: availableOnly } }),
  createDriver: (data: { name: string; experience_years: number }) =>
    apiClient.post<VirtualDriver>('/fleet/drivers', data),
  assignDriver: (vehicleId: string, driverId: string) =>
    apiClient.post(`/fleet/vehicles/${vehicleId}/assign-driver`, { driver_id: driverId }),
  stats: () => apiClient.get('/fleet/stats'),
};

export const routingApi = {
  listMissions: (status?: string) =>
    apiClient.get<Mission[]>('/missions', { params: status ? { status } : {} }),
  createMission: (data: {
    origin_lat: number; origin_lng: number; dest_lat: number; dest_lng: number;
    priority?: number; cargo_description?: string;
  }) => apiClient.post<Mission>('/missions', data),
  assignMission: (missionId: string, vehicleId: string) =>
    apiClient.post(`/missions/${missionId}/assign`, { vehicle_id: vehicleId }),
  completeMission: (missionId: string) => apiClient.post(`/missions/${missionId}/complete`),
  cancelMission: (missionId: string) => apiClient.post(`/missions/${missionId}/cancel`),
};

export const trackingApi = {
  live: () => apiClient.get<Telemetry[]>('/tracking/live'),
  latest: (vehicleId: string) => apiClient.get<Telemetry>(`/tracking/vehicles/${vehicleId}/latest`),
  history: (vehicleId: string, limit = 100) =>
    apiClient.get<Telemetry[]>(`/tracking/vehicles/${vehicleId}/history`, { params: { limit } }),
};

export const notificationApi = {
  list: () => apiClient.get<Notification[]>('/notifications'),
  markRead: (id: string) => apiClient.post(`/notifications/${id}/read`),
  listIncidents: () => apiClient.get<Incident[]>('/notifications/incidents'),
  resolveIncident: (id: string) => apiClient.post<Incident>(`/notifications/incidents/${id}/resolve`),
};

export const analyticsApi = {
  summary: () => apiClient.get<DashboardSummary>('/analytics/public/summary'),
  fleet: () => apiClient.get('/analytics/fleet'),
  missions: () => apiClient.get('/analytics/missions'),
  incidents: () => apiClient.get('/analytics/incidents'),
  dashboard: () => apiClient.get<DashboardSummary>('/analytics/dashboard'),
};

export const tasksApi = {
  optimizeRoutes: () => apiClient.post('/tasks/optimize-routes'),
  scheduleMaintenance: () => apiClient.post('/tasks/schedule-maintenance'),
  computeAnalytics: () => apiClient.post('/tasks/compute-analytics'),
};
