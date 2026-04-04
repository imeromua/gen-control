'use client';

import { useState, useEffect } from 'react';
import { Download, BarChart2, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

type Generator = { id: number; name: string };

const MONTHS = [
  'Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
  'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень',
];

export default function ReportsPage() {
  const [generators, setGenerators] = useState<Generator[]>([]);
  const [genId,   setGenId]   = useState('');
  const [year,    setYear]    = useState(new Date().getFullYear());
  const [month,   setMonth]   = useState(new Date().getMonth() + 1);
  const [price,   setPrice]   = useState(50);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  useEffect(() => {
    api.getGenerators().then((data: unknown) => {
      const list = (
        Array.isArray(data) ? data
          : (data as { items?: unknown[] }).items ?? []
      ) as Generator[];
      setGenerators(list);
      if (list.length > 0) setGenId(String(list[0].id));
    }).catch(() => {});
  }, []);

  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i);

  const handleDownload = async () => {
    if (!genId) return;
    setLoading(true);
    setError('');
    try {
      const blob = await api.downloadMonthlyReport({
        generatorId: genId,
        year,
        month,
        fuelPrice: price,
      });
      const url = URL.createObjectURL(blob);
      const a   = document.createElement('a');
      a.href     = url;
      a.download = `zvit_${genId}_${year}_${String(month).padStart(2, '0')}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Помилка завантаження');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto space-y-6">

      {/* Заголовок */}
      <div className="flex items-center gap-3">
        <BarChart2 className="h-6 w-6 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">Звіти</h1>
          <p className="text-sm text-muted-foreground">
            Генерація місячного звіту у форматі Excel (.xlsx)
          </p>
        </div>
      </div>

      {/* Форма */}
      <div className="rounded-xl border bg-card p-6 space-y-4 shadow-sm">

        {/* Генератор */}
        <div className="space-y-1">
          <label className="text-sm font-medium">Генератор</label>
          <select
            className="w-full rounded-lg border bg-background px-3 py-2 text-sm"
            value={genId}
            onChange={e => setGenId(e.target.value)}
          >
            {generators.map(g => (
              <option key={g.id} value={g.id}>{g.name}</option>
            ))}
          </select>
        </div>

        {/* Рік + Місяць */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Рік</label>
            <select
              className="w-full rounded-lg border bg-background px-3 py-2 text-sm"
              value={year}
              onChange={e => setYear(Number(e.target.value))}
            >
              {years.map(y => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium">Місяць</label>
            <select
              className="w-full rounded-lg border bg-background px-3 py-2 text-sm"
              value={month}
              onChange={e => setMonth(Number(e.target.value))}
            >
              {MONTHS.map((m, i) => (
                <option key={i + 1} value={i + 1}>{m}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Ціна палива */}
        <div className="space-y-1">
          <label className="text-sm font-medium">Ціна палива (грн/л)</label>
          <input
            type="number"
            min={0}
            step={0.5}
            className="w-full rounded-lg border bg-background px-3 py-2 text-sm"
            value={price}
            onChange={e => setPrice(Number(e.target.value))}
          />
        </div>

        {/* Помилка */}
        {error && (
          <p className="text-sm text-destructive bg-destructive/10 rounded-lg px-3 py-2">
            {error}
          </p>
        )}

        {/* Кнопка */}
        <button
          onClick={handleDownload}
          disabled={loading || !genId}
          className="w-full flex items-center justify-center gap-2 rounded-lg
                     bg-primary text-primary-foreground px-4 py-2.5 text-sm
                     font-medium hover:bg-primary/90 disabled:opacity-50
                     disabled:cursor-not-allowed transition-colors"
        >
          {loading
            ? <><Loader2 className="h-4 w-4 animate-spin" /> Генерація…</>
            : <><Download className="h-4 w-4" /> Завантажити звіт .xlsx</>
          }
        </button>
      </div>

      {/* Підказка */}
      <div className="text-xs text-muted-foreground space-y-1 px-1">
        <p>📋 Звіт містить три аркуші:</p>
        <ul className="list-disc list-inside space-y-0.5 ml-2">
          <li><strong>Операційний журнал</strong> — деталізація по зміні/добі</li>
          <li><strong>Зведення місяця</strong> — ключові показники та щоденна таблиця</li>
          <li><strong>Технічне обслуговування</strong> — журнал ТО та залишок ресурсу</li>
        </ul>
      </div>
    </div>
  );
}
