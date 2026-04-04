'use client';
import { useState } from 'react';
import useSWR from 'swr';
import { AppLayout } from '@/components/AppLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import { Download, FileSpreadsheet, Loader2, AlertCircle } from 'lucide-react';

interface Generator { id: string; name: string; is_active: boolean; }

export default function ReportsPage() {
  const now = new Date();
  const [generatorId, setGeneratorId] = useState('');
  const [year,  setYear]  = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [fuelPrice, setFuelPrice] = useState(50);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string | null>(null);

  const { data: generators } = useSWR<Generator[]>('generators', () => api.getGenerators());

  const UA_MONTHS = ['', 'Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
                     'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'];

  const handleDownload = async () => {
    if (!generatorId) { setError('Оберіть генератор'); return; }
    setLoading(true);
    setError(null);
    try {
      const blob = await api.downloadMonthlyReport({ generatorId, year, month, fuelPrice });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = `Zvit-${String(month).padStart(2, '0')}.${year}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      setError('Помилка генерації звіту. Спробуйте ще раз.');
    } finally {
      setLoading(false);
    }
  };

  const genObj = generators?.find(g => g.id === generatorId);

  return (
    <AppLayout>
      <div className="p-4 max-w-xl mx-auto space-y-6">
        <h1 className="text-xl font-bold">Звіти</h1>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <FileSpreadsheet className="h-5 w-5 text-green-600" />
              Місячний звіт Excel
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">

            {/* Генератор */}
            <div className="space-y-1.5">
              <Label htmlFor="gen-select">Генератор</Label>
              <select
                id="gen-select"
                className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={generatorId}
                onChange={e => setGeneratorId(e.target.value)}
              >
                <option value="">— Оберіть генератор —</option>
                {(generators || []).map(g => (
                  <option key={g.id} value={g.id}>
                    {g.name}{!g.is_active ? ' (неактивний)' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Місяць / Рік */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="month-select">Місяць</Label>
                <select
                  id="month-select"
                  className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={month}
                  onChange={e => setMonth(Number(e.target.value))}
                >
                  {UA_MONTHS.slice(1).map((m, i) => (
                    <option key={i + 1} value={i + 1}>{m}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="year-input">Рік</Label>
                <Input
                  id="year-input"
                  type="number"
                  min={2020}
                  max={2099}
                  value={year}
                  onChange={e => setYear(Number(e.target.value))}
                />
              </div>
            </div>

            {/* Ціна палива */}
            <div className="space-y-1.5">
              <Label htmlFor="fuel-price">Ціна палива (грн/л)</Label>
              <Input
                id="fuel-price"
                type="number"
                min={1}
                step={0.5}
                value={fuelPrice}
                onChange={e => setFuelPrice(Number(e.target.value))}
              />
            </div>

            {/* Попередній перегляд параметрів */}
            {generatorId && (
              <div className="rounded-lg bg-muted/50 border px-4 py-3 text-sm space-y-1">
                <p><span className="text-muted-foreground">Генератор:</span> <strong>{genObj?.name}</strong></p>
                <p><span className="text-muted-foreground">Період:</span> <strong>{UA_MONTHS[month]} {year}</strong></p>
                <p><span className="text-muted-foreground">Ціна палива:</span> <strong>{fuelPrice} грн/л</strong></p>
              </div>
            )}

            {/* Помилка */}
            {error && (
              <div className="flex items-center gap-2 text-sm text-red-600 rounded-lg bg-red-50 border border-red-200 px-3 py-2">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                {error}
              </div>
            )}

            {/* Кнопка */}
            <Button
              onClick={handleDownload}
              disabled={!generatorId || loading}
              className="w-full"
            >
              {loading ? (
                <><Loader2 className="h-4 w-4 animate-spin mr-2" />Формування…</>
              ) : (
                <><Download className="h-4 w-4 mr-2" />Завантажити .xlsx</>
              )}
            </Button>

            <p className="text-xs text-muted-foreground text-center">
              Файл містить: Операційний журнал · Зведення місяця · Технічне обслуговування
            </p>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
