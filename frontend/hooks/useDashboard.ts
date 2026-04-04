'use client';
import useSWR from 'swr';
import { api } from '@/lib/api';
import type { DashboardData } from '@/types/api';

export function useDashboard() {
  const { data, error, isLoading, mutate } = useSWR<DashboardData>(
    'dashboard',
    () => api.dashboard() as Promise<DashboardData>,
    { refreshInterval: 30000 }
  );
  return { data, error, isLoading, mutate };
}
