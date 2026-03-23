'use client';
import { useState } from 'react';
import useSWR from 'swr';
import { useAuth } from '@/hooks/useAuth';
import { AppLayout } from '@/components/AppLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { api } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import { toast } from '@/hooks/useToast';
import { Plus, Trash2, Calendar } from 'lucide-react';

interface OutageItem {
  id: number;
  start_time: string;
  end_time: string;
  duration_hours?: number;
  note?: string;
}

export default function OutagePage() {
  const { user } = useAuth();
  const isAdmin = (user as { role?: { name?: string } } | null)?.role?.name === 'ADMIN';
  const { data, mutate } = useSWR('outage', () => api.getOutageSchedule());
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ start_time: '', end_time: '', note: '' });
  const [loading, setLoading] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.addOutage(form as Record<string, unknown>);
      toast({ title: 'Відключення додано' });
      setOpen(false);
      setForm({ start_time: '', end_time: '', note: '' });
      mutate();
    } catch (err: unknown) {
      toast({ title: 'Помилка', description: err instanceof Error ? err.message : 'Невідома помилка', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.deleteOutage(id);
      toast({ title: 'Відключення видалено' });
      mutate();
    } catch (err: unknown) {
      toast({ title: 'Помилка', description: err instanceof Error ? err.message : 'Невідома помилка', variant: 'destructive' });
    }
    setDeleteId(null);
  };

  const items: OutageItem[] = Array.isArray(data) ? data : ((data as { items?: OutageItem[] })?.items || []);

  return (
    <AppLayout>
      <div className="p-4 max-w-4xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">Графік відключень</h1>
          {isAdmin && (
            <Dialog open={open} onOpenChange={setOpen}>
              <DialogTrigger asChild>
                <Button size="sm"><Plus className="h-4 w-4 mr-1" /> Додати</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>Додати відключення</DialogTitle></DialogHeader>
                <form onSubmit={handleAdd} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Початок</Label>
                    <Input type="datetime-local" value={form.start_time} onChange={e => setForm(f => ({ ...f, start_time: e.target.value }))} required />
                  </div>
                  <div className="space-y-2">
                    <Label>Кінець</Label>
                    <Input type="datetime-local" value={form.end_time} onChange={e => setForm(f => ({ ...f, end_time: e.target.value }))} required />
                  </div>
                  <div className="space-y-2">
                    <Label>Примітка</Label>
                    <Textarea value={form.note} onChange={e => setForm(f => ({ ...f, note: e.target.value }))} />
                  </div>
                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? 'Зберігаємо...' : 'Зберегти'}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          )}
        </div>

        {items.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground">Немає запланованих відключень</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {items.map((item) => {
              const start = new Date(item.start_time);
              const end = new Date(item.end_time);
              const isUpcoming = start > new Date();
              const isActive = start <= new Date() && end >= new Date();
              return (
                <Card key={item.id} className={isActive ? 'border-orange-500' : ''}>
                  <CardContent className="py-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          {isActive && <span className="h-2 w-2 rounded-full bg-orange-500 animate-pulse" />}
                          {isUpcoming && <span className="h-2 w-2 rounded-full bg-blue-500" />}
                          <span className="font-medium text-sm">
                            {formatDateTime(item.start_time)} — {formatDateTime(item.end_time)}
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Тривалість: {item.duration_hours ? `${item.duration_hours} год` : `${((end.getTime() - start.getTime()) / 3600000).toFixed(1)} год`}
                          {item.note && ` • ${item.note}`}
                        </div>
                        {isActive && <div className="text-xs text-orange-500 font-medium">● Зараз активне</div>}
                        {isUpcoming && <div className="text-xs text-blue-500">Заплановано</div>}
                      </div>
                      {isAdmin && (
                        <div>
                          {deleteId === item.id ? (
                            <div className="flex gap-1">
                              <Button size="sm" variant="destructive" onClick={() => handleDelete(item.id)}>✓</Button>
                              <Button size="sm" variant="outline" onClick={() => setDeleteId(null)}>✗</Button>
                            </div>
                          ) : (
                            <Button size="sm" variant="ghost" onClick={() => setDeleteId(item.id)}>
                              <Trash2 className="h-4 w-4 text-muted-foreground" />
                            </Button>
                          )}
                        </div>
                      )}
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
