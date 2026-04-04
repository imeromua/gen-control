'use client';
import { useState } from 'react';
import useSWR from 'swr';
import { AppLayout } from '@/components/AppLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/api';
import { formatDateTime, formatDuration, formatLiters } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface Shift {
  id: string;               // UUID
  shift_number: number;
  generator_id: string;     // UUID
  generator_name?: string;  // joined on backend (if present)
  started_by: string | null;
  started_by_name?: string; // joined on backend (if present)
  started_at: string;
  stopped_at: string | null;
  duration_minutes: string | number | null;
  fuel_consumed_liters: string | number | null;
  status: string;           // 'active' | 'stopped'
}

/** Show first 8 chars of UUID when no human-readable name is available */
function shortUuid(uuid: string | null | undefined): string {
  if (!uuid) return '—';
  return uuid.slice(0, 8) + '…';
}

function durationSeconds(minutes: string | number | null): number | null {
  if (minutes === null || minutes === undefined) return null;
  return Math.round(Number(minutes) * 60);
}

export default function ShiftsPage() {
  const [dateFilter, setDateFilter] = useState('');
  const { data, isLoading } = useSWR(['shifts', dateFilter], () =>
    api.getShifts(dateFilter ? `date=${dateFilter}` : '')
  );

  const shifts: Shift[] = Array.isArray(data)
    ? (data as Shift[])
    : ((data as { items?: Shift[] })?.items ?? []);

  return (
    <AppLayout>
      <div className="p-4 max-w-5xl mx-auto space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <h1 className="text-xl font-bold">Журнал змін</h1>
          <div className="flex items-center gap-2">
            <Label htmlFor="date-filter" className="text-sm">Дата:</Label>
            <Input
              id="date-filter"
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-auto"
            />
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-20 rounded-xl bg-muted animate-pulse" />
            ))}
          </div>
        ) : shifts.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              Змін не знайдено
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Desktop table */}
            <div className="hidden lg:block">
              <Card>
                <CardContent className="p-0 overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-4 font-medium text-muted-foreground">#</th>
                        <th className="text-left p-4 font-medium text-muted-foreground">Генератор</th>
                        <th className="text-left p-4 font-medium text-muted-foreground">Початок</th>
                        <th className="text-left p-4 font-medium text-muted-foreground">Кінець</th>
                        <th className="text-left p-4 font-medium text-muted-foreground">Тривалість</th>
                        <th className="text-left p-4 font-medium text-muted-foreground">Паливо</th>
                        <th className="text-left p-4 font-medium text-muted-foreground">Оператор</th>
                      </tr>
                    </thead>
                    <tbody>
                      {shifts.map((shift) => {
                        const durSec = durationSeconds(shift.duration_minutes);
                        const isActive = shift.status === 'active';
                        return (
                          <tr key={shift.id} className="border-b last:border-0 hover:bg-muted/30">
                            <td className="p-4 tabular-nums font-medium">{shift.shift_number}</td>
                            <td className="p-4">
                              {shift.generator_name
                                ? shift.generator_name
                                : <span className="text-muted-foreground font-mono text-xs">{shortUuid(shift.generator_id)}</span>
                              }
                            </td>
                            <td className="p-4 tabular-nums">{formatDateTime(shift.started_at)}</td>
                            <td className="p-4 tabular-nums">
                              {isActive
                                ? <span className="text-green-500 font-medium">Активна</span>
                                : shift.stopped_at ? formatDateTime(shift.stopped_at) : '—'
                              }
                            </td>
                            <td className="p-4 tabular-nums">
                              {durSec !== null ? formatDuration(durSec) : isActive ? <span className="text-muted-foreground">—</span> : '—'}
                            </td>
                            <td className="p-4 tabular-nums">
                              {shift.fuel_consumed_liters != null
                                ? formatLiters(Number(shift.fuel_consumed_liters))
                                : '—'
                              }
                            </td>
                            <td className="p-4">
                              {shift.started_by_name
                                ? shift.started_by_name
                                : shift.started_by
                                  ? <span className="text-muted-foreground font-mono text-xs">{shortUuid(shift.started_by)}</span>
                                  : '—'
                              }
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </CardContent>
              </Card>
            </div>

            {/* Mobile cards */}
            <div className="lg:hidden space-y-3">
              {shifts.map((shift) => {
                const durSec = durationSeconds(shift.duration_minutes);
                const isActive = shift.status === 'active';
                return (
                  <Card key={shift.id}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">
                        Зміна #{shift.shift_number}
                        {' — '}
                        {shift.generator_name
                          ? shift.generator_name
                          : <span className="font-mono text-xs">{shortUuid(shift.generator_id)}</span>
                        }
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Початок</span>
                        <span className="tabular-nums">{formatDateTime(shift.started_at)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Кінець</span>
                        <span>
                          {isActive
                            ? <span className="text-green-500 font-medium">Активна</span>
                            : shift.stopped_at ? formatDateTime(shift.stopped_at) : '—'
                          }
                        </span>
                      </div>
                      {durSec !== null && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Тривалість</span>
                          <span className="tabular-nums">{formatDuration(durSec)}</span>
                        </div>
                      )}
                      {shift.fuel_consumed_liters != null && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Паливо</span>
                          <span className="tabular-nums">{formatLiters(Number(shift.fuel_consumed_liters))}</span>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Оператор</span>
                        <span>
                          {shift.started_by_name
                            ? shift.started_by_name
                            : shift.started_by
                              ? <span className="font-mono text-xs">{shortUuid(shift.started_by)}</span>
                              : '—'
                          }
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </>
        )}
      </div>
    </AppLayout>
  );
}
