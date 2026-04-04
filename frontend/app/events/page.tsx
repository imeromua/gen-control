'use client';
import { useState } from 'react';
import useSWR from 'swr';
import { AppLayout } from '@/components/AppLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { api } from '@/lib/api';
import { formatDateTime, formatLiters } from '@/lib/utils';
import {
  CheckCircle2, Clock, Fuel, Wrench, AlertTriangle, AlertCircle,
  FileText, Settings, Plus, RefreshCw, PowerOff, Zap
} from 'lucide-react';

// ---- Типи подій (реальні значення з EventType enum) ----------------------
const EVENT_LABELS: Record<string, string> = {
  SHIFT_STARTED:             'Початок зміни',
  SHIFT_STOPPED:             'Кінець зміни',
  FUEL_DELIVERED:            'Постачання палива',
  FUEL_REFILLED:             'Заправка',
  FUEL_STOCK_UPDATED:        'Оновлення запасу палива',
  OIL_STOCK_UPDATED:         'Оновлення запасу масла',
  MAINTENANCE_PERFORMED:     'Технічне обслуговування',
  GENERATOR_CREATED:         'Додано генератор',
  GENERATOR_UPDATED:         'Оновлено генератор',
  GENERATOR_SETTINGS_UPDATED:'Налаштування генератора',
  GENERATOR_DEACTIVATED:     'Генератор деактивовано',
  SYSTEM_SETTINGS_UPDATED:   'Налаштування системи',
  ADJUSTMENT_CREATED:        'Коригування даних',
};

const EVENT_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  SHIFT_STARTED:             CheckCircle2,
  SHIFT_STOPPED:             Clock,
  FUEL_DELIVERED:            Fuel,
  FUEL_REFILLED:             RefreshCw,
  FUEL_STOCK_UPDATED:        Fuel,
  OIL_STOCK_UPDATED:         Fuel,
  MAINTENANCE_PERFORMED:     Wrench,
  GENERATOR_CREATED:         Plus,
  GENERATOR_UPDATED:         Settings,
  GENERATOR_SETTINGS_UPDATED:Settings,
  GENERATOR_DEACTIVATED:     PowerOff,
  SYSTEM_SETTINGS_UPDATED:   Settings,
  ADJUSTMENT_CREATED:        FileText,
};

const EVENT_COLORS: Record<string, string> = {
  SHIFT_STARTED:             'text-green-500',
  SHIFT_STOPPED:             'text-blue-500',
  FUEL_DELIVERED:            'text-yellow-500',
  FUEL_REFILLED:             'text-orange-500',
  FUEL_STOCK_UPDATED:        'text-yellow-400',
  OIL_STOCK_UPDATED:         'text-amber-500',
  MAINTENANCE_PERFORMED:     'text-purple-500',
  GENERATOR_CREATED:         'text-teal-500',
  GENERATOR_UPDATED:         'text-sky-500',
  GENERATOR_SETTINGS_UPDATED:'text-sky-400',
  GENERATOR_DEACTIVATED:     'text-red-500',
  SYSTEM_SETTINGS_UPDATED:   'text-muted-foreground',
  ADJUSTMENT_CREATED:        'text-indigo-400',
};

// Фільтр у select — лише ті типи, за якими користувачі будуть фільтрувати
const FILTER_OPTIONS: Array<{ value: string; label: string }> = [
  { value: 'SHIFT_STARTED',             label: 'Початок зміни' },
  { value: 'SHIFT_STOPPED',             label: 'Кінець зміни' },
  { value: 'FUEL_DELIVERED',            label: 'Постачання' },
  { value: 'FUEL_REFILLED',             label: 'Заправка' },
  { value: 'MAINTENANCE_PERFORMED',     label: 'ТО' },
  { value: 'GENERATOR_DEACTIVATED',     label: 'Деактивація' },
  { value: 'ADJUSTMENT_CREATED',        label: 'Коригування' },
];

interface EventMeta {
  generator_name?: string;
  shift_number?: number;
  duration_minutes?: number;
  fuel_consumed_liters?: number;
  fuel_consumed_estimate_liters?: number;
  liters?: number;
  liters_added?: number;
  work_time_start?: string;
  work_time_end?: string;
  [key: string]: unknown;
}

interface EventItem {
  id: string;
  event_type: string;
  generator_id: string | null;
  performed_by: string | null;
  meta: EventMeta | null;
  created_at: string;
  // якщо бекенд join-ітиме потім:
  generator_name?: string;
  performed_by_name?: string;
}

/** Мета → читабельний опис події */
function buildDescription(type: string, meta: EventMeta | null): string | null {
  if (!meta) return null;
  switch (type) {
    case 'SHIFT_STARTED':
      return meta.shift_number ? `Зміна #${meta.shift_number}` : null;
    case 'SHIFT_STOPPED': {
      const parts: string[] = [];
      if (meta.shift_number)      parts.push(`Зміна #${meta.shift_number}`);
      if (meta.duration_minutes != null)
        parts.push(`Тривалість: ${(meta.duration_minutes / 60).toFixed(2)} год`);
      if (meta.fuel_consumed_liters != null)
        parts.push(`Паливо: ${formatLiters(meta.fuel_consumed_liters)}`);
      return parts.join(' • ') || null;
    }
    case 'FUEL_DELIVERED':
    case 'FUEL_REFILLED': {
      const l = meta.liters ?? meta.liters_added;
      return l != null ? formatLiters(Number(l)) : null;
    }
    case 'SYSTEM_SETTINGS_UPDATED':
      return meta.work_time_start && meta.work_time_end
        ? `Робочий час: ${meta.work_time_start} – ${meta.work_time_end}`
        : null;
    default:
      return null;
  }
}

/** Назва генератора: спочатку з meta, потім joined field */
function generatorLabel(event: EventItem): string | null {
  if (event.generator_name) return event.generator_name;
  if (event.meta?.generator_name) return event.meta.generator_name;
  if (event.generator_id) return event.generator_id.slice(0, 8) + '…';
  return null;
}

export default function EventsPage() {
  const [typeFilter, setTypeFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');

  const params = [
    typeFilter ? `event_type=${typeFilter}` : '',
    dateFilter ? `date=${dateFilter}` : '',
  ].filter(Boolean).join('&');

  const { data, isLoading } = useSWR(['events', params], () => api.getEvents(params));
  const events: EventItem[] = Array.isArray(data)
    ? (data as EventItem[])
    : ((data as { items?: EventItem[] })?.items ?? []);

  return (
    <AppLayout>
      <div className="p-4 max-w-4xl mx-auto space-y-4">
        <h1 className="text-xl font-bold">Журнал подій</h1>

        {/* Фільтри */}
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <Label htmlFor="type-filter" className="text-sm whitespace-nowrap">Тип події:</Label>
            <select
              id="type-filter"
              className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={typeFilter}
              onChange={e => setTypeFilter(e.target.value)}
            >
              <option value="">Усі</option>
              {FILTER_OPTIONS.map(({ value, label }) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <Label htmlFor="date-filter" className="text-sm">Дата:</Label>
            <Input
              id="date-filter"
              type="date"
              value={dateFilter}
              onChange={e => setDateFilter(e.target.value)}
              className="w-auto"
            />
          </div>
        </div>

        {/* Список */}
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-16 rounded-xl bg-muted animate-pulse" />
            ))}
          </div>
        ) : events.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground">Подій не знайдено</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-2">
            {events.map((event) => {
              const Icon = EVENT_ICONS[event.event_type] || AlertCircle;
              const color = EVENT_COLORS[event.event_type] || 'text-muted-foreground';
              const label = EVENT_LABELS[event.event_type] || event.event_type;
              const genName = generatorLabel(event);
              const desc = buildDescription(event.event_type, event.meta);

              return (
                <Card key={event.id}>
                  <CardContent className="py-3 px-4">
                    <div className="flex items-start gap-3">
                      <Icon className={`h-5 w-5 mt-0.5 flex-shrink-0 ${color}`} />
                      <div className="flex-1 min-w-0">
                        {/* Головний рядок: лейбл + генератор */}
                        <div className="text-sm font-medium">
                          {label}
                          {genName && (
                            <>
                              <span className="text-muted-foreground font-normal mx-1">•</span>
                              <span className="text-muted-foreground font-normal">{genName}</span>
                            </>
                          )}
                        </div>
                        {/* Деталі з meta */}
                        {desc && (
                          <div className="text-xs text-muted-foreground mt-0.5">{desc}</div>
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground flex-shrink-0 tabular-nums">
                        {formatDateTime(event.created_at)}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
