import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { formatDistanceToNow, format } from 'date-fns';
import { uk } from 'date-fns/locale';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

/**
 * Formats a number (or string/Decimal from the backend) as liters.
 * Backend returns Decimal fields as strings (e.g. "123.45"), so we
 * always coerce to Number before calling toFixed.
 */
export function formatLiters(liters: number | string | null | undefined): string {
  const n = Number(liters);
  if (isNaN(n)) return '— л';
  return `${n.toFixed(1)} л`;
}

export function formatDateRelative(dateStr: string): string {
  return formatDistanceToNow(new Date(dateStr), { addSuffix: true, locale: uk });
}

export function formatDateTime(dateStr: string): string {
  return format(new Date(dateStr), 'dd.MM.yyyy HH:mm', { locale: uk });
}

export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

export function setAuthToken(token: string): void {
  localStorage.setItem('access_token', token);
}

export function removeAuthToken(): void {
  localStorage.removeItem('access_token');
}
