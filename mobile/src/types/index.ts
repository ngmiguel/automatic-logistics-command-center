export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'operator' | 'dispatcher' | 'analyst';
  is_active: boolean;
}

export interface Vehicle {
  id: string;
  license_plate: string;
  model: string;
  state: string;
  fuel_level: number;
  latitude: number;
  longitude: number;
  speed_kmh: number;
  driver_id: string | null;
  mission_id: string | null;
}

export interface VirtualDriver {
  id: string;
  name: string;
  status: string;
  vehicle_id: string | null;
  experience_years: number;
}

export interface Mission {
  id: string;
  origin_lat: number;
  origin_lng: number;
  dest_lat: number;
  dest_lng: number;
  status: string;
  vehicle_id: string | null;
  priority: number;
  cargo_description: string;
  estimated_distance_km: number;
}

export interface Telemetry {
  vehicle_id: string;
  latitude: number;
  longitude: number;
  speed_kmh: number;
  fuel_level: number;
  state: string;
  recorded_at: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  severity: string;
  vehicle_id: string | null;
  is_read: boolean;
}

export interface Incident {
  id: string;
  vehicle_id: string;
  severity: string;
  description: string;
  resolved: boolean;
}

export interface FleetKPIs {
  total_vehicles: number;
  en_route_vehicles: number;
  incident_vehicles: number;
  fleet_utilization_rate: number;
  average_fuel_level: number;
  average_speed_kmh: number;
  idle_vehicles: number;
  maintenance_vehicles: number;
}

export interface DashboardSummary {
  fleet: FleetKPIs;
  missions: Record<string, number | string>;
  incidents: Record<string, number | string>;
}

export interface WsMessage {
  channel: string;
  data: Telemetry | { title: string; message: string; severity: string };
}

export type VehicleVariant = 'executive' | 'crossover' | 'hauler';

export const MODEL_VARIANTS: Record<string, VehicleVariant> = {
  'AutoHauler M5': 'executive',
  'AutoVan Z3': 'crossover',
  'AutoTruck X1': 'hauler',
};

export const VARIANT_LABELS: Record<VehicleVariant, { name: string; brand: string; color: string }> = {
  executive: { name: 'Executive Sedan', brand: 'Inspired M-Series', color: '#1e40af' },
  crossover: { name: 'Urban Crossover', brand: 'Inspired X-Drive', color: '#059669' },
  hauler: { name: 'Autonomous Hauler', brand: 'Inspired i-Freight', color: '#7c3aed' },
};
