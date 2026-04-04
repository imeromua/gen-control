export interface User {
  id: string;
  full_name: string;
  username: string;
  role: { id: number; name: string };
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Shift {
  id: string;
  generator_id: string;
  generator_name?: string;
  started_at: string;
  ended_at?: string;
  fuel_used_liters?: number;
  motohours?: number;
  started_by?: string;
}

// Matches GeneratorDashboardSchema from backend dashboard/schemas.py
export interface GeneratorDashboard {
  id: string;                        // UUID
  name: string;
  type: string;
  is_active: boolean;
  motohours_total: number;
  motohours_since_last_to: number;
  hours_to_next_to: number | null;
  to_warning_active: boolean;
  fuel_type: string | null;
  tank_capacity_liters: number | null;
}

// Matches GeneratorStatusResponse from backend generators/schemas.py
export interface GeneratorStatus {
  generator_id: string;              // UUID
  name: string;
  type: string;
  is_active: boolean;
  fuel_type: string | null;
  tank_capacity_liters: number | null;
  current_fuel_liters: number | null;
  motohours_total: number;
  motohours_since_last_to: number;
  next_to_at_hours: number | null;
  hours_to_next_to: number | null;
  to_warning_active: boolean;
  fuel_warning_active: boolean;
  fuel_critical_active: boolean;
}

// Matches GeneratorResponse from backend generators/schemas.py (list endpoint)
export interface GeneratorBase {
  id: string;                        // UUID
  name: string;
  type: string;
  model: string | null;
  serial_number: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FuelStock {
  fuel_type: string;
  current_liters: number;
  max_limit_liters: number;
  warning_level_liters: number;
  warning_active: boolean;
  critical_active: boolean;
}

export interface FuelDelivery {
  id: string;
  liters: number;
  delivered_at: string;
  note?: string;
}

export interface FuelRefill {
  id: string;
  generator_id: string;
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

// Matches NextOutageSchema
export interface NextOutage {
  outage_date: string;   // date string
  hour_start: number;
  hour_end: number;
  note: string | null;
}

// Matches RecentEventSchema
export interface EventLog {
  id: string;            // UUID
  event_type: string;
  generator_name: string | null;
  created_at: string;
  meta: Record<string, unknown> | null;
}

// Matches ActiveShiftSchema
export interface ActiveShift {
  id: string;
  shift_number: number;
  generator_id: string;
  generator_name: string;
  started_at: string;
  started_by_name: string | null;
  duration_minutes: number;
  fuel_consumed_estimate_liters: number | null;
}

// Matches TodayStatsSchema
export interface TodayStats {
  shifts_count: number;
  total_hours_worked: number;
  total_fuel_consumed_liters: number;
  total_fuel_delivered_liters: number;
  maintenance_performed: boolean;
}

// Matches DashboardResponse (GET /api/dashboard)
export interface DashboardData {
  generated_at: string;
  active_shift: ActiveShift | null;
  generators: GeneratorDashboard[];
  fuel_stock: FuelStock | null;
  oil_stocks: unknown[];
  next_outage: NextOutage | null;
  today_stats: TodayStats;
  recent_events: EventLog[];
}
