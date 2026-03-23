'use client';
import { useState } from 'react';
import useSWR from 'swr';
import { AppLayout } from '@/components/AppLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { api } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import {
  CheckCircle2, Clock, Fuel, Settings, AlertTriangle, AlertCircle, FileText
} from 'lucide-react';

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

const EVENT_TYPE_LABELS: Record<string, string> = {
  SHIFT_START: 'Початок зміни',
  SHIFT_STOP: 'Кінець зміни',
  FUEL_DELIVERY: 'Постачання',
  FUEL_REFILL: 'Заправка',
  MAINTENANCE: 'ТО',
  OUTAGE_START: 'Відключення',
  OUTAGE_END: 'Підключення',
};

interface EventItem {
  id: number;
  event_type: string;
  description: string;
  created_at: string;
  generator_id?: number;
}

export default function EventsPage() {
  const [typeFilter, setTypeFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');

  const params = [
    typeFilter ? `event_type=${typeFilter}` : '',
    dateFilter ? `date=${dateFilter}` : '',
  ].filter(Boolean).join('&');

  const { data, isLoading } = useSWR(['events', params], () => api.getEvents(params));
  const events: EventItem[] = Array.isArray(data) ? data : ((data as { items?: EventItem[] })?.items || []);

  return (
    <AppLayout>
      <div className="p-4 max-w-4xl mx-auto space-y-4">
        <h1 className="text-xl font-bold">Журнал подій</h1>
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
              {Object.entries(EVENT_TYPE_LABELS).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <Label htmlFor="date-filter" className="text-sm">Дата:</Label>
            <Input id="date-filter" type="date" value={dateFilter} onChange={e => setDateFilter(e.target.value)} className="w-auto" />
          </div>
        </div>

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
              return (
                <Card key={event.id}>
                  <CardContent className="py-3 px-4">
                    <div className="flex items-start gap-3">
                      <Icon className={`h-5 w-5 mt-0.5 flex-shrink-0 ${color}`} />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium">{event.description}</div>
                        <div className="text-xs text-muted-foreground mt-0.5">
                          {EVENT_TYPE_LABELS[event.event_type] || event.event_type}
                          {event.generator_id && ` • Генератор #${event.generator_id}`}
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground flex-shrink-0">
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
