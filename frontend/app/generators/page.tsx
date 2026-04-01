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

interface GeneratorData {
  id: number;
  name: string;
  fuel_consumption_l_per_h: number;
  motohours_total: number;
  maintenance_interval_h: number;
  motohours_since_maintenance: number;
}

export default function GeneratorsPage() {
  const { user } = useAuth();
  const isAdmin = (user as { role?: { name?: string } } | null)?.role?.name === 'ADMIN';
  const { data: generators, mutate } = useSWR('generators', () => api.getGenerators());
  const [maintNote, setMaintNote] = useState('');
  const [maintOpen, setMaintOpen] = useState<number | null>(null);
  const [maintLoading, setMaintLoading] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [editData, setEditData] = useState<{ fuel_consumption_l_per_h?: number; maintenance_interval_h?: number }>({});
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

  const handleMaintenance = async (genId: number) => {
    setMaintLoading(true);
    try {
      await api.recordMaintenance(genId, { note: maintNote });
      toast({ title: 'ТО зафіксовано' });
      setMaintOpen(null);
      setMaintNote('');
      mutate();
    } catch (err: unknown) {
      toast({ title: 'Помилка', description: err instanceof Error ? err.message : 'Невідома помилка', variant: 'destructive' });
    } finally {
      setMaintLoading(false);
    }
  };

  const handleEdit = async (genId: number) => {
    setEditLoading(true);
    try {
      await api.updateGenerator(genId, editData as Record<string, unknown>);
      toast({ title: 'Налаштування збережено' });
      setEditId(null);
      setEditData({});
      mutate();
    } catch (err: unknown) {
      toast({ title: 'Помилка', description: err instanceof Error ? err.message : 'Невідома помилка', variant: 'destructive' });
    } finally {
      setEditLoading(false);
    }
  };

  const genArr: GeneratorData[] = Array.isArray(generators) ? generators : [];

  return (
    <AppLayout>
      <div className="p-4 max-w-4xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">Генератори</h1>
          {isAdmin && (
            <Button onClick={() => setCreateOpen(true)}>+ Додати генератор</Button>
          )}
        </div>
        
        <CreateGeneratorDialog 
          open={createOpen} 
          onOpenChange={setCreateOpen} 
          onSuccess={() => mutate()} 
        />

        {genArr.map((gen) => {
          const toMaintenance = gen.maintenance_interval_h - gen.motohours_since_maintenance;
          const maintPct = Math.min(Math.round((gen.motohours_since_maintenance / gen.maintenance_interval_h) * 100), 100);
          const needsMaintenance = toMaintenance <= 10;

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
                      if (o) setEditData({
                        fuel_consumption_l_per_h: gen.fuel_consumption_l_per_h,
                        maintenance_interval_h: gen.maintenance_interval_h,
                      });
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
                              value={editData.fuel_consumption_l_per_h || ''}
                              onChange={e => setEditData(d => ({ ...d, fuel_consumption_l_per_h: parseFloat(e.target.value) }))}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Інтервал ТО (год)</Label>
                            <Input
                              type="number"
                              step="1"
                              value={editData.maintenance_interval_h || ''}
                              onChange={e => setEditData(d => ({ ...d, maintenance_interval_h: parseFloat(e.target.value) }))}
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
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Мотогодини всього</span>
                    <div className="font-bold">{gen.motohours_total?.toFixed(1)} год</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Витрата</span>
                    <div className="font-bold">{gen.fuel_consumption_l_per_h} л/год</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">До ТО залишилось</span>
                    <div className={`font-bold ${needsMaintenance ? 'text-red-500' : ''}`}>
                      {toMaintenance.toFixed(1)} год
                    </div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Інтервал ТО</span>
                    <div className="font-bold">{gen.maintenance_interval_h} год</div>
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
              </CardContent>
            </Card>
          );
        })}
        {genArr.length === 0 && (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              Генераторів не знайдено
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}
