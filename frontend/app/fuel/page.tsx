'use client';
import { useState } from 'react';
import useSWR from 'swr';
import { AppLayout } from '@/components/AppLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { api } from '@/lib/api';
import { formatLiters, formatDateTime } from '@/lib/utils';
import { toast } from '@/hooks/useToast';
import { AlertTriangle, Plus, Fuel } from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid
} from 'recharts';
import { format, subDays } from 'date-fns';
import { uk } from 'date-fns/locale';

interface FuelStockData {
  current_liters: number;
  max_limit_liters: number;
  warning_level_liters: number;
  fuel_type: string;
}

interface FuelRefillItem {
  id: number;
  liters: number;
  refilled_at: string;
}

interface FuelDeliveryItem {
  id: number;
  liters: number;
  delivered_at: string;
  note?: string;
}

interface GeneratorItem {
  id: number;
  name: string;
}

export default function FuelPage() {
  const { data: stock, mutate: mutateStock } = useSWR<FuelStockData>('fuel-stock', () => api.getFuelStock() as Promise<FuelStockData>);
  const { data: deliveries, mutate: mutateDeliveries } = useSWR('fuel-deliveries', () => api.getFuelDeliveries());
  const { data: refills, mutate: mutateRefills } = useSWR('fuel-refills', () => api.getFuelRefills());

  const [deliveryLiters, setDeliveryLiters] = useState('');
  const [deliveryNote, setDeliveryNote] = useState('');
  const [deliveryOpen, setDeliveryOpen] = useState(false);
  const [deliveryLoading, setDeliveryLoading] = useState(false);

  const [refillGenId, setRefillGenId] = useState('');
  const [refillLiters, setRefillLiters] = useState('');
  const [refillLevelBefore, setRefillLevelBefore] = useState('');
  const [refillOpen, setRefillOpen] = useState(false);
  const [refillLoading, setRefillLoading] = useState(false);

  const { data: generators } = useSWR('generators', () => api.getGenerators());

  const handleDelivery = async (e: React.FormEvent) => {
    e.preventDefault();
    setDeliveryLoading(true);
    try {
      await api.addFuelDelivery({ liters: parseFloat(deliveryLiters), note: deliveryNote });
      toast({ title: 'Паливо прийнято', description: `${formatLiters(parseFloat(deliveryLiters))}` });
      setDeliveryOpen(false);
      setDeliveryLiters('');
      setDeliveryNote('');
      mutateStock();
      mutateDeliveries();
    } catch (err: unknown) {
      toast({ title: 'Помилка', description: err instanceof Error ? err.message : 'Невідома помилка', variant: 'destructive' });
    } finally {
      setDeliveryLoading(false);
    }
  };

  const handleRefill = async (e: React.FormEvent) => {
    e.preventDefault();
    setRefillLoading(true);
    try {
      await api.addFuelRefill({
        generator_id: parseInt(refillGenId),
        liters: parseFloat(refillLiters),
        level_before: refillLevelBefore ? parseFloat(refillLevelBefore) : undefined,
      });
      toast({ title: 'Генератор заправлено', description: `${formatLiters(parseFloat(refillLiters))}` });
      setRefillOpen(false);
      setRefillLiters('');
      setRefillLevelBefore('');
      mutateStock();
      mutateRefills();
    } catch (err: unknown) {
      toast({ title: 'Помилка', description: err instanceof Error ? err.message : 'Невідома помилка', variant: 'destructive' });
    } finally {
      setRefillLoading(false);
    }
  };

  const fuelPct = stock ? Math.round((stock.current_liters / stock.max_limit_liters) * 100) : 0;
  const isLowFuel = stock && stock.current_liters <= stock.warning_level_liters;

  const refillsArr: FuelRefillItem[] = Array.isArray(refills) ? refills : ((refills as { items?: FuelRefillItem[] })?.items || []);
  const chartData = Array.from({ length: 7 }).map((_, i) => {
    const day = subDays(new Date(), 6 - i);
    const dayStr = format(day, 'yyyy-MM-dd');
    const liters = refillsArr
      .filter((r) => r.refilled_at?.startsWith(dayStr))
      .reduce((sum, r) => sum + (r.liters || 0), 0);
    return { date: format(day, 'dd.MM', { locale: uk }), liters };
  });

  const deliveriesArr: FuelDeliveryItem[] = Array.isArray(deliveries) ? deliveries : [];
  const generatorsArr: GeneratorItem[] = Array.isArray(generators) ? generators : [];

  return (
    <AppLayout>
      <div className="p-4 max-w-4xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">Паливо</h1>
          <div className="flex gap-2">
            <Dialog open={deliveryOpen} onOpenChange={setDeliveryOpen}>
              <DialogTrigger asChild>
                <Button size="sm"><Plus className="h-4 w-4 mr-1" /> Прийняти</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>Прийняти паливо</DialogTitle></DialogHeader>
                <form onSubmit={handleDelivery} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Кількість (л)</Label>
                    <Input type="number" step="0.1" min="0.1" value={deliveryLiters} onChange={e => setDeliveryLiters(e.target.value)} required />
                  </div>
                  <div className="space-y-2">
                    <Label>Примітка</Label>
                    <Textarea value={deliveryNote} onChange={e => setDeliveryNote(e.target.value)} />
                  </div>
                  <Button type="submit" className="w-full" disabled={deliveryLoading}>
                    {deliveryLoading ? 'Зберігаємо...' : 'Зберегти'}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>

            <Dialog open={refillOpen} onOpenChange={setRefillOpen}>
              <DialogTrigger asChild>
                <Button size="sm" variant="outline"><Fuel className="h-4 w-4 mr-1" /> Заправити</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>Заправити генератор</DialogTitle></DialogHeader>
                <form onSubmit={handleRefill} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Генератор</Label>
                    <select
                      className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={refillGenId}
                      onChange={e => setRefillGenId(e.target.value)}
                      required
                    >
                      <option value="">Оберіть генератор</option>
                      {generatorsArr.map((g) => (
                        <option key={g.id} value={g.id}>{g.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label>Літри</Label>
                    <Input type="number" step="0.1" min="0.1" value={refillLiters} onChange={e => setRefillLiters(e.target.value)} required />
                  </div>
                  <div className="space-y-2">
                    <Label>Рівень до (л, необов&apos;язково)</Label>
                    <Input type="number" step="0.1" min="0" value={refillLevelBefore} onChange={e => setRefillLevelBefore(e.target.value)} />
                  </div>
                  <Button type="submit" className="w-full" disabled={refillLoading}>
                    {refillLoading ? 'Зберігаємо...' : 'Зберегти'}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-sm">Склад палива</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {stock ? (
              <>
                <div className="flex justify-between text-sm">
                  <span className={isLowFuel ? 'text-yellow-500 font-bold' : ''}>
                    {formatLiters(stock.current_liters)}
                  </span>
                  <span className="text-muted-foreground">{formatLiters(stock.max_limit_liters)}</span>
                </div>
                <Progress value={fuelPct} className={isLowFuel ? '[&>div]:bg-yellow-500' : ''} />
                {isLowFuel && (
                  <div className="flex items-center gap-1 text-xs text-yellow-600">
                    <AlertTriangle className="h-3 w-3" />
                    Поріг попередження: {formatLiters(stock.warning_level_liters)}
                  </div>
                )}
                <div className="text-xs text-muted-foreground">Тип: {stock.fuel_type}</div>
              </>
            ) : (
              <div className="h-16 bg-muted animate-pulse rounded" />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-sm">Витрати палива (7 днів)</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v: number) => [`${v} л`, 'Витрата']} />
                <Bar dataKey="liters" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-sm">Постачання</CardTitle></CardHeader>
          <CardContent>
            {deliveriesArr.length === 0 ? (
              <p className="text-sm text-muted-foreground">Немає записів</p>
            ) : (
              <div className="space-y-2">
                {deliveriesArr.map((d) => (
                  <div key={d.id} className="flex justify-between text-sm py-1 border-b last:border-0">
                    <span>{formatDateTime(d.delivered_at)}</span>
                    <span className="font-medium text-green-500">+{formatLiters(d.liters)}</span>
                    {d.note && <span className="text-muted-foreground text-xs">{d.note}</span>}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-sm">Заправки генераторів</CardTitle></CardHeader>
          <CardContent>
            {refillsArr.length === 0 ? (
              <p className="text-sm text-muted-foreground">Немає записів</p>
            ) : (
              <div className="space-y-2">
                {refillsArr.map((r) => (
                  <div key={r.id} className="flex justify-between text-sm py-1 border-b last:border-0">
                    <span>{formatDateTime(r.refilled_at)}</span>
                    <span className="font-medium text-orange-500">−{formatLiters(r.liters)}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
