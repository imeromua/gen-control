'use client';
import useSWR from 'swr';
import { api } from '@/lib/api';
import type { DashboardSummary } from '@/types/api';

export function useDashboard() {
  const { data, error, isLoading, mutate } = useSWR<DashboardSummary>(
    'dashboard-summary',
    () => api.dashboardSummary() as Promise<DashboardSummary>,
    { refreshInterval: 30000 }
  );
  return { data, error, isLoading, mutate };
}
