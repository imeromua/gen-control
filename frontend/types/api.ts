export interface User {
  id: number;
  full_name: string;
  username: string;
  role: { id: number; name: string };
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Shift {
  id: number;
  generator_id: number;
  generator_name?: string;
  started_at: string;
  ended_at?: string;
  fuel_used_liters?: number;
  motohours?: number;
  started_by?: string;
}

export interface Generator {
  id: number;
  name: string;
  fuel_consumption_l_per_h: number;
  motohours_total: number;
  maintenance_interval_h: number;
  motohours_since_maintenance: number;
  low_fuel_threshold_l?: number;
  critical_fuel_threshold_l?: number;
}

export interface FuelStock {
  id: number;
  fuel_type: string;
  current_liters: number;
  max_limit_liters: number;
  warning_level_liters: number;
}

export interface FuelDelivery {
  id: number;
  liters: number;
  delivered_at: string;
  note?: string;
}

export interface FuelRefill {
  id: number;
  generator_id: number;
  liters: number;
  level_before?: number;
  refilled_at: string;
}

export interface OutageSchedule {
  id: number;
  start_time: string;
  end_time: string;
  duration_hours: number;
  note?: string;
}

export interface EventLog {
  id: number;
  event_type: string;
  description: string;
  created_at: string;
  generator_id?: number;
}

export interface DashboardSummary {
  active_shift?: {
    id: number;
    generator_name: string;
    started_at: string;
    fuel_used_liters: number;
    motohours: number;
    started_by: string;
  };
  fuel_stock?: FuelStock;
  generators: Generator[];
  next_outage?: OutageSchedule;
  today_stats: {
    shifts_count: number;
    total_hours: number;
    total_fuel_liters: number;
  };
  recent_events: EventLog[];
}
