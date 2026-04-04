import { getAuthToken } from './utils';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    throw new Error('Unauthorized');
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error((body as { detail?: string }).detail || `Error ${res.status}`);
  }
  if (res.status === 204) return null as unknown as T;
  return res.json();
}

export const api = {
  // Auth
  login: (username: string, password: string) =>
    request<{ access_token: string; token_type: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),
  me: () => request<User>('/api/auth/me'),
  logout: () => request<void>('/api/auth/logout', { method: 'POST' }),

  // Dashboard
  // GET /api/dashboard — повна відповідь з generators[], fuel_stock, active_shift і т.д.
  dashboard: () => request<DashboardData>('/api/dashboard'),
  // GET /api/dashboard/summary — спрощена відповідь БЕЗ generators (лише для статус-бару)
  dashboardSummary: () => request<DashboardSummaryData>('/api/dashboard/summary'),

  // Shifts
  getShifts: (params?: string) => request<ShiftList>(`/api/shifts${params ? '?' + params : ''}`),
  startShift: (data: Record<string, unknown>) => request<ShiftItem>('/api/shifts/start', { method: 'POST', body: JSON.stringify(data) }),
  stopShift: () => request<ShiftItem>('/api/shifts/stop', { method: 'POST' }),

  // Fuel
  getFuelStock: () => request<FuelStockData>('/api/fuel/stock'),
  getFuelDeliveries: () => request<FuelDeliveryList>('/api/fuel/deliveries'),
  getFuelRefills: () => request<FuelRefillList>('/api/fuel/refills'),
  addFuelDelivery: (data: Record<string, unknown>) => request<FuelDeliveryItem>('/api/fuel/deliveries', { method: 'POST', body: JSON.stringify(data) }),
  addFuelRefill: (data: Record<string, unknown>) => request<FuelRefillItem>('/api/fuel/refills', { method: 'POST', body: JSON.stringify(data) }),

  // Generators
  // GET /api/generators — список базових даних (id, name, type, is_active, ...)
  getGenerators: () => request<GeneratorList>('/api/generators'),
  // GET /api/generators/{id}/status — повний статус (motohours, TO, паливо)
  getGeneratorStatus: (id: string) => request<GeneratorStatusData>(`/api/generators/${id}/status`),
  createGenerator: (data: Record<string, unknown>) =>
    request<GeneratorItem>('/api/generators', { method: 'POST', body: JSON.stringify(data) }),
  updateGenerator: (id: string | number, data: Record<string, unknown>) =>
    request<GeneratorItem>(`/api/generators/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  updateGeneratorSettings: (id: string | number, data: Record<string, unknown>) =>
    request<GeneratorItem>(`/api/generators/${id}/settings`, { method: 'PUT', body: JSON.stringify(data) }),
  recordMaintenance: (id: string | number, data: Record<string, unknown>) =>
    request<GeneratorItem>(`/api/generators/${id}/maintenance`, { method: 'POST', body: JSON.stringify(data) }),

  // Outage
  getOutageSchedule: () => request<OutageList>('/api/outage/schedule'),
  addOutage: (data: Record<string, unknown>) => request<OutageItem>('/api/outage/schedule', { method: 'POST', body: JSON.stringify(data) }),
  deleteOutage: (id: number) => request<void>(`/api/outage/schedule/${id}`, { method: 'DELETE' }),

  // Events
  getEvents: (params?: string) => request<EventList>(`/api/events${params ? '?' + params : ''}`),
};

// Loose types for API responses
type User = Record<string, unknown>;
type DashboardData = Record<string, unknown>;
type DashboardSummaryData = Record<string, unknown>;
type ShiftList = Record<string, unknown> | unknown[];
type ShiftItem = Record<string, unknown>;
type FuelStockData = Record<string, unknown>;
type FuelDeliveryList = Record<string, unknown> | unknown[];
type FuelRefillList = Record<string, unknown> | unknown[];
type FuelDeliveryItem = Record<string, unknown>;
type FuelRefillItem = Record<string, unknown>;
type GeneratorList = Record<string, unknown> | unknown[];
type GeneratorItem = Record<string, unknown>;
type GeneratorStatusData = Record<string, unknown>;
type OutageList = Record<string, unknown> | unknown[];
type OutageItem = Record<string, unknown>;
type EventList = Record<string, unknown> | unknown[];
