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
  id: number;
  generator_id: number;
  generator_name?: string;
  started_at: string;
  ended_at?: string;
  fuel_used_liters?: number;
  started_by?: string;
}

export default function ShiftsPage() {
  const [dateFilter, setDateFilter] = useState('');
  const { data, isLoading } = useSWR(['shifts', dateFilter], () =>
    api.getShifts(dateFilter ? `date=${dateFilter}` : '')
  );

  const shifts: Shift[] = Array.isArray(data) ? data : ((data as { items?: Shift[] })?.items || []);

  return (
    <AppLayout>
      <div className="p-4 max-w-5xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
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
          <Card><CardContent className="py-8 text-center text-muted-foreground">Змін не знайдено</CardContent></Card>
        ) : (
          <>
            {/* Desktop table */}
            <div className="hidden lg:block">
              <Card>
                <CardContent className="p-0">
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
                        const dur = shift.ended_at
                          ? Math.floor((new Date(shift.ended_at).getTime() - new Date(shift.started_at).getTime()) / 1000)
                          : null;
                        return (
                          <tr key={shift.id} className="border-b last:border-0 hover:bg-muted/30">
                            <td className="p-4">{shift.id}</td>
                            <td className="p-4">{shift.generator_name || `#${shift.generator_id}`}</td>
                            <td className="p-4">{formatDateTime(shift.started_at)}</td>
                            <td className="p-4">{shift.ended_at ? formatDateTime(shift.ended_at) : <span className="text-green-500">Активна</span>}</td>
                            <td className="p-4">{dur !== null ? formatDuration(dur) : '—'}</td>
                            <td className="p-4">{shift.fuel_used_liters ? formatLiters(shift.fuel_used_liters) : '—'}</td>
                            <td className="p-4">{shift.started_by || '—'}</td>
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
                const dur = shift.ended_at
                  ? Math.floor((new Date(shift.ended_at).getTime() - new Date(shift.started_at).getTime()) / 1000)
                  : null;
                return (
                  <Card key={shift.id}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">Зміна #{shift.id} — {shift.generator_name || `Генератор #${shift.generator_id}`}</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Початок</span>
                        <span>{formatDateTime(shift.started_at)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Кінець</span>
                        <span>{shift.ended_at ? formatDateTime(shift.ended_at) : <span className="text-green-500">Активна</span>}</span>
                      </div>
                      {dur !== null && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Тривалість</span>
                          <span>{formatDuration(dur)}</span>
                        </div>
                      )}
                      {shift.fuel_used_liters && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Паливо</span>
                          <span>{formatLiters(shift.fuel_used_liters)}</span>
                        </div>
                      )}
                      {shift.started_by && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Оператор</span>
                          <span>{shift.started_by}</span>
                        </div>
                      )}
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
