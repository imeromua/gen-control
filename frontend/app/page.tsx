'use client';
import { AppLayout } from '@/components/AppLayout';
import { useDashboard } from '@/hooks/useDashboard';
import { useShiftTimer } from '@/hooks/useShiftTimer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { formatDuration, formatLiters, formatDateRelative } from '@/lib/utils';
import { api } from '@/lib/api';
import { toast } from '@/hooks/useToast';
import { useState } from 'react';
import {
  Zap, Clock, Fuel, Settings, AlertTriangle, Calendar,
  CheckCircle2, Activity, TrendingDown, AlertCircle
} from 'lucide-react';
import type { GeneratorDashboard, EventLog } from '@/types/api';

const EVENT_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  SHIFT_START: CheckCircle2,
  SHIFT_STOP: Clock,
  FUEL_DELIVERY: Fuel,
  FUEL_REFILL: Fuel,
  MAINTENANCE: Settings,
  OUTAGE_START: AlertTriangle,
  OUTAGE_END: CheckCircle2,
};

const EVENT_COLORS: Record<string, string> = {
  SHIFT_START: 'text-green-500',
  SHIFT_STOP: 'text-blue-500',
  FUEL_DELIVERY: 'text-yellow-500',
  FUEL_REFILL: 'text-orange-500',
  MAINTENANCE: 'text-purple-500',
  OUTAGE_START: 'text-red-500',
  OUTAGE_END: 'text-green-500',
};

export default function DashboardPage() {
  const { data, isLoading, mutate } = useDashboard();
  const elapsed = useShiftTimer(data?.active_shift?.started_at);
  const [confirming, setConfirming] = useState<'start' | 'stop' | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const handleStart = async () => {
    if (confirming !== 'start') { setConfirming('start'); return; }
    setConfirming(null);
    setActionLoading(true);
    try {
      const generators = data?.generators || [];
      if (generators.length === 0) throw new Error('Немає активних генераторів');
      await api.startShift({ generator_id: generators[0].id });
      toast({ title: 'Зміну розпочато', description: `Генератор ${generators[0].name}` });
      mutate();
    } catch (err: unknown) {
      toast({ title: 'Помилка', description: err instanceof Error ? err.message : 'Невідома помилка', variant: 'destructive' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleStop = async () => {
    if (confirming !== 'stop') { setConfirming('stop'); return; }
    setConfirming(null);
    setActionLoading(true);
    try {
      // Бекенд: POST /shifts/{shift_id}/stop — shift_id обов'язковий
      const shiftId = data?.active_shift?.id;
      if (!shiftId) throw new Error('Немає активної зміни');
      await api.stopShift(shiftId);
      toast({ title: 'Зміну завершено' });
      mutate();
    } catch (err: unknown) {
      toast({ title: 'Помилка', description: err instanceof Error ? err.message : 'Невідома помилка', variant: 'destructive' });
    } finally {
      setActionLoading(false);
    }
  };

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-4 space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-32 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      </AppLayout>
    );
  }

  const fuelPct = data?.fuel_stock
    ? Math.round((Number(data.fuel_stock.current_liters) / Number(data.fuel_stock.max_limit_liters)) * 100)
    : 0;
  const isLowFuel = data?.fuel_stock?.warning_active;
  const isCriticalFuel = data?.fuel_stock?.critical_active;

  return (
    <AppLayout>
      <div className="p-4 space-y-4 max-w-6xl mx-auto">
        {/* Start/Stop */}
        <Card>
          <CardContent className="p-6">
            {data?.active_shift ? (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-green-500">
                  <Activity className="h-5 w-5 animate-pulse" />
                  <span className="font-semibold">Активна зміна #{data.active_shift.shift_number}</span>
                </div>
                <div className="text-4xl font-mono font-bold tracking-wider">
                  {formatDuration(elapsed)}
                </div>
                <div className="text-sm text-muted-foreground">
                  {data.active_shift.generator_name}
                  {data.active_shift.started_by_name ? ` • Запустив: ${data.active_shift.started_by_name}` : ''}
                </div>
                <div className="text-sm">
                  Паливо (оцінка): <strong>{formatLiters(data.active_shift.fuel_consumed_estimate_liters ?? 0)}</strong>
                  {' • '}
                  Тривалість: <strong>{(Number(data.active_shift.duration_minutes) / 60).toFixed(2)} год</strong>
                </div>
                {confirming === 'stop' ? (
                  <div className="flex gap-2">
                    <Button variant="destructive" onClick={handleStop} disabled={actionLoading} className="flex-1">
                      ⚠️ Підтвердити зупинку
                    </Button>
                    <Button variant="outline" onClick={() => setConfirming(null)} className="flex-1">
                      Скасувати
                    </Button>
                  </div>
                ) : (
                  <Button variant="destructive" onClick={handleStop} disabled={actionLoading} className="w-full lg:w-auto">
                    ⏹ Зупинити генератор
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Zap className="h-5 w-5" />
                  <span>Генератор не працює</span>
                </div>
                {confirming === 'start' ? (
                  <div className="flex gap-2">
                    <Button onClick={handleStart} disabled={actionLoading} className="flex-1">
                      ✅ Підтвердити запуск
                    </Button>
                    <Button variant="outline" onClick={() => setConfirming(null)} className="flex-1">
                      Скасувати
                    </Button>
                  </div>
                ) : (
                  <Button onClick={handleStart} disabled={actionLoading} size="lg" className="w-full lg:w-auto">
                    ▶️ Запустити генератор
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Fuel Stock */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Fuel className="h-4 w-4" />
                Запас палива
              </CardTitle>
            </CardHeader>
            <CardContent>
              {data?.fuel_stock ? (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className={isCriticalFuel ? 'text-red-500 font-bold' : isLowFuel ? 'text-yellow-500 font-bold' : ''}>
                      {formatLiters(data.fuel_stock.current_liters)}
                    </span>
                    <span className="text-muted-foreground">{formatLiters(data.fuel_stock.max_limit_liters)}</span>
                  </div>
                  <Progress
                    value={fuelPct}
                    className={isCriticalFuel ? '[&>div]:bg-red-500' : isLowFuel ? '[&>div]:bg-yellow-500' : ''}
                  />
                  {isLowFuel && (
                    <div className="flex items-center gap-1 text-xs text-yellow-600">
                      <AlertTriangle className="h-3 w-3" />
                      Низький рівень палива
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-muted-foreground text-sm">Дані відсутні</p>
              )}
            </CardContent>
          </Card>

          {/* Today Stats */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <TrendingDown className="h-4 w-4" />
                Сьогодні
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Змін</span>
                  <strong>{data?.today_stats?.shifts_count ?? 0}</strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Годин роботи</span>
                  <strong>{Number(data?.today_stats?.total_hours_worked ?? 0).toFixed(1)}</strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Витрачено палива</span>
                  <strong>{formatLiters(data?.today_stats?.total_fuel_consumed_liters ?? 0)}</strong>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Next Outage */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Наступне відключення
              </CardTitle>
            </CardHeader>
            <CardContent>
              {data?.next_outage ? (
                <div className="space-y-1 text-sm">
                  <div className="font-semibold">{data.next_outage.outage_date}</div>
                  <div className="text-muted-foreground">
                    {data.next_outage.hour_start}:00 – {data.next_outage.hour_end}:00
                  </div>
                  {data.next_outage.note && (
                    <div className="text-xs text-muted-foreground">{data.next_outage.note}</div>
                  )}
                </div>
              ) : (
                <p className="text-muted-foreground text-sm">Немає запланованих</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Generators */}
        {data?.generators && data.generators.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {data.generators.map((gen: GeneratorDashboard) => {
              const toHours = gen.hours_to_next_to ?? null;
              const motoSinceTo = Number(gen.motohours_since_last_to);
              const maintPct = toHours != null
                ? Math.min(Math.round((motoSinceTo / (motoSinceTo + Number(toHours))) * 100), 100)
                : 0;
              return (
                <Card key={gen.id}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Zap className="h-4 w-4 text-yellow-500" />
                      {gen.name}
                      <span className="text-xs text-muted-foreground ml-auto">{gen.type}</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="text-sm">
                      <span className="text-muted-foreground">Мотогодини: </span>
                      <strong>{Number(gen.motohours_total).toFixed(1)} год</strong>
                    </div>
                    <div className="text-sm flex justify-between">
                      <span className="text-muted-foreground">До ТО:</span>
                      <span className={gen.to_warning_active ? 'text-red-500 font-bold' : ''}>
                        {toHours != null ? `${Number(toHours).toFixed(1)} год` : '—'}
                      </span>
                    </div>
                    <Progress value={maintPct} className={gen.to_warning_active ? '[&>div]:bg-red-500' : ''} />
                    {gen.to_warning_active && (
                      <div className="flex items-center gap-1 text-xs text-red-500">
                        <AlertCircle className="h-3 w-3" />
                        Необхідне технічне обслуговування
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Recent Events */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Останні події</CardTitle>
          </CardHeader>
          <CardContent>
            {data?.recent_events && data.recent_events.length > 0 ? (
              <div className="space-y-2">
                {data.recent_events.slice(0, 10).map((event: EventLog) => {
                  const Icon = EVENT_ICONS[event.event_type] || AlertCircle;
                  const color = EVENT_COLORS[event.event_type] || 'text-muted-foreground';
                  return (
                    <div key={event.id} className="flex items-start gap-2 text-sm">
                      <Icon className={`h-4 w-4 mt-0.5 flex-shrink-0 ${color}`} />
                      <div className="flex-1 min-w-0">
                        <span className="truncate">
                          {event.generator_name ? `[${event.generator_name}] ` : ''}
                          {event.event_type.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <span className="text-xs text-muted-foreground flex-shrink-0">
                        {formatDateRelative(event.created_at)}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Немає подій</p>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
