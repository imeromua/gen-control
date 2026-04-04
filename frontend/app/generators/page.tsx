'use client';
import { useState } from 'react';
import useSWR from 'swr';
import { useAuth } from '@/hooks/useAuth';
import { AppLayout } from '@/components/AppLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { api } from '@/lib/api';
import { toast } from '@/hooks/useToast';
import { AlertCircle, Settings, CheckCircle2, Lock } from 'lucide-react';
import { CreateGeneratorDialog } from '@/components/generators/CreateGeneratorDialog';
import type { GeneratorBase, GeneratorStatus } from '@/types/api';

export default function GeneratorsPage() {
  const { user } = useAuth();
  const isAdmin = (user as { role?: { name?: string } } | null)?.role?.name === 'ADMIN';

  // Список генераторів (базові дані)
  const { data: generators, mutate } = useSWR<GeneratorBase[]>(
    'generators-list',
    () => api.getGenerators() as Promise<GeneratorBase[]>
  );

  // Статус кожного генератора (мотогодини, ТО)
  const genIds = (generators ?? []).map((g) => g.id);
  const { data: statusMap, mutate: mutateStatus } = useSWR<Record<string, GeneratorStatus>>(
    genIds.length > 0 ? ['generators-status', ...genIds] : null,
    async () => {
      const entries = await Promise.all(
        genIds.map(async (id) => {
          const status = await api.getGeneratorStatus(id) as GeneratorStatus;
          return [id, status] as [string, GeneratorStatus];
        })
      );
      return Object.fromEntries(entries);
    }
  );

  const [maintNote, setMaintNote] = useState('');
  const [maintOpen, setMaintOpen] = useState<string | null>(null);
  const [maintLoading, setMaintLoading] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [editData, setEditData] = useState<{ fuel_consumption_per_hour?: number; to_interval_hours?: number }>({});
  const [editLoading, setEditLoading] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);

  if (!isAdmin) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center h-full p-4 text-center">
          <Lock className="h-16 w-16 text-muted-foreground mb-4" />
          <h2 className="text-xl font-bold">Доступ заборонено</h2>
          <p className="text-muted-foreground">Ця сторінка доступна лише адміністраторам</p>
        </div>
      </AppLayout>
    );
  }

  const handleMaintenance = async (genId: string) => {
    setMaintLoading(true);
    try {
      await api.recordMaintenance(genId, { note: maintNote });
      toast({ title: 'ТО зафіксовано' });
      setMaintOpen(null);
      setMaintNote('');
      mutateStatus();
    } catch (err: unknown) {
      toast({ title: 'Помилка', description: err instanceof Error ? err.message : 'Невідома помилка', variant: 'destructive' });
    } finally {
      setMaintLoading(false);
    }
  };

  const handleEdit = async (genId: string) => {
    setEditLoading(true);
    try {
      await api.updateGeneratorSettings(genId, editData as Record<string, unknown>);
      toast({ title: 'Налаштування збережено' });
      setEditId(null);
      setEditData({});
      mutateStatus();
    } catch (err: unknown) {
      toast({ title: 'Помилка', description: err instanceof Error ? err.message : 'Невідома помилка', variant: 'destructive' });
    } finally {
      setEditLoading(false);
    }
  };

  const genArr: GeneratorBase[] = Array.isArray(generators) ? generators : [];

  return (
    <AppLayout>
      <div className="p-4 max-w-4xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">Генератори</h1>
          <Button onClick={() => setCreateOpen(true)}>+ Додати генератор</Button>
        </div>

        <CreateGeneratorDialog
          open={createOpen}
          onOpenChange={setCreateOpen}
          onSuccess={() => { mutate(); mutateStatus(); }}
        />

        {genArr.map((gen) => {
          const st: GeneratorStatus | undefined = statusMap?.[gen.id];
          const toHours = st?.hours_to_next_to ?? null;
          const motoTotal = st?.motohours_total ?? 0;
          const motoSinceTo = st?.motohours_since_last_to ?? 0;
          const maintPct = toHours != null
            ? Math.min(Math.round((motoSinceTo / (motoSinceTo + toHours)) * 100), 100)
            : 0;
          const needsMaintenance = st?.to_warning_active ?? false;
          const fuelConsumption = st
            ? null  // GeneratorStatus не містить fuel_consumption, беремо з settings через окремий запит якщо потрібно
            : null;

          return (
            <Card key={gen.id}>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center justify-between">
                  <span>{gen.name}</span>
                  <div className="flex gap-2">
                    <Dialog open={maintOpen === gen.id} onOpenChange={(o) => setMaintOpen(o ? gen.id : null)}>
                      <DialogTrigger asChild>
                        <Button size="sm" variant={needsMaintenance ? 'destructive' : 'outline'}>
                          <CheckCircle2 className="h-4 w-4 mr-1" />
                          Зафіксувати ТО
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader><DialogTitle>Зафіксувати ТО — {gen.name}</DialogTitle></DialogHeader>
                        <div className="space-y-4">
                          <div className="space-y-2">
                            <Label>Примітка</Label>
                            <Textarea value={maintNote} onChange={e => setMaintNote(e.target.value)} placeholder="Описання виконаних робіт..." />
                          </div>
                          <Button
                            className="w-full"
                            onClick={() => handleMaintenance(gen.id)}
                            disabled={maintLoading}
                          >
                            {maintLoading ? 'Зберігаємо...' : 'Підтвердити ТО'}
                          </Button>
                        </div>
                      </DialogContent>
                    </Dialog>

                    <Dialog open={editId === gen.id} onOpenChange={(o) => {
                      setEditId(o ? gen.id : null);
                      if (o) setEditData({});
                    }}>
                      <DialogTrigger asChild>
                        <Button size="sm" variant="ghost"><Settings className="h-4 w-4" /></Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader><DialogTitle>Налаштування — {gen.name}</DialogTitle></DialogHeader>
                        <div className="space-y-4">
                          <div className="space-y-2">
                            <Label>Витрата палива (л/год)</Label>
                            <Input
                              type="number"
                              step="0.01"
                              value={editData.fuel_consumption_per_hour ?? ''}
                              onChange={e => setEditData(d => ({ ...d, fuel_consumption_per_hour: parseFloat(e.target.value) }))}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Інтервал ТО (год)</Label>
                            <Input
                              type="number"
                              step="1"
                              value={editData.to_interval_hours ?? ''}
                              onChange={e => setEditData(d => ({ ...d, to_interval_hours: parseFloat(e.target.value) }))}
                            />
                          </div>
                          <Button className="w-full" onClick={() => handleEdit(gen.id)} disabled={editLoading}>
                            {editLoading ? 'Зберігаємо...' : 'Зберегти'}
                          </Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {!st ? (
                  <div className="text-sm text-muted-foreground animate-pulse">Завантаження даних...</div>
                ) : (
                  <>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Мотогодини всього</span>
                        <div className="font-bold">{Number(motoTotal).toFixed(1)} год</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Тип палива</span>
                        <div className="font-bold">{st.fuel_type ?? '—'}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">До ТО залишилось</span>
                        <div className={`font-bold ${needsMaintenance ? 'text-red-500' : ''}`}>
                          {toHours != null ? `${Number(toHours).toFixed(1)} год` : '—'}
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">З останнього ТО</span>
                        <div className="font-bold">{Number(motoSinceTo).toFixed(1)} год</div>
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Прогрес до ТО</span>
                        <span>{maintPct}%</span>
                      </div>
                      <Progress value={maintPct} className={needsMaintenance ? '[&>div]:bg-red-500' : ''} />
                    </div>
                    {needsMaintenance && (
                      <div className="flex items-center gap-1 text-xs text-red-500">
                        <AlertCircle className="h-3 w-3" />
                        Необхідне технічне обслуговування!
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          );
        })}

        {genArr.length === 0 && (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              Генераторів не знайдено. Натисніть «+ Додати генератор».
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}
