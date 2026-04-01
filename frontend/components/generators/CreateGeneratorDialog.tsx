'use client';
import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { api } from '@/lib/api';
import { toast } from '@/hooks/useToast';
import { Loader2 } from 'lucide-react';

interface CreateGeneratorDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function CreateGeneratorDialog({ open, onOpenChange, onSuccess }: CreateGeneratorDialogProps) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Step 1: Base
  const [name, setName] = useState('');
  const [type, setType] = useState('MAIN');
  const [model, setModel] = useState('');
  const [serialNumber, setSerialNumber] = useState('');

  // Step 2: Fuel
  const [fuelType, setFuelType] = useState('DIESEL');
  const [tankCapacity, setTankCapacity] = useState('');
  const [fuelConsumption, setFuelConsumption] = useState('');

  // Step 3: Maintenance
  const [maintenanceInterval, setMaintenanceInterval] = useState('200');
  const [toWarningBefore, setToWarningBefore] = useState('10');
  const [initialMotohours, setInitialMotohours] = useState('0');

  const selectClassName = "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50";

  const handleNext = () => setStep(s => s + 1);
  const handlePrev = () => setStep(s => s - 1);

  const handleSubmit = async () => {
    if (!name.trim()) {
      toast({ title: 'Помилка', description: 'Назва генератора обов\'язкова', variant: 'destructive' });
      return;
    }

    setLoading(true);
    try {
      // 1. Create generator
      const genObj = await api.createGenerator({
        name,
        type,
        model: model || null,
        serial_number: serialNumber || null,
      });

      // 2. Update settings
      const settingsData = {
        fuel_type: fuelType,
        tank_capacity_liters: tankCapacity ? parseFloat(tankCapacity) : null,
        fuel_consumption_per_hour: fuelConsumption ? parseFloat(fuelConsumption) : null,
        to_interval_hours: maintenanceInterval ? parseFloat(maintenanceInterval) : null,
        to_warning_before_hours: toWarningBefore ? parseFloat(toWarningBefore) : null,
        initial_motohours: initialMotohours ? parseFloat(initialMotohours) : 0,
      };

      await api.updateGeneratorSettings(genObj.id as string, settingsData);

      toast({ title: 'Генератор успішно створено' });
      
      // Reset state
      setStep(1);
      setName('');
      setType('MAIN');
      setModel('');
      setSerialNumber('');
      setFuelType('DIESEL');
      setTankCapacity('');
      setFuelConsumption('');
      setMaintenanceInterval('200');
      setToWarningBefore('10');
      setInitialMotohours('0');
      
      onSuccess();
      onOpenChange(false);
    } catch (err: unknown) {
      toast({ 
        title: 'Помилка при створенні', 
        description: err instanceof Error ? err.message : 'Невідома помилка', 
        variant: 'destructive' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Додати новий генератор - Крок {step} з 3</DialogTitle>
        </DialogHeader>

        <div className="py-4">
          {step === 1 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Назва (обов'язково)</Label>
                <Input value={name} onChange={(e: any) => setName(e.target.value)} placeholder="Генератор №1" />
              </div>
              <div className="space-y-2">
                <Label>Тип використання</Label>
                <select className={selectClassName} value={type} onChange={(e: any) => setType(e.target.value)}>
                  <option value="MAIN">Основний (MAIN)</option>
                  <option value="BACKUP">Резервний (BACKUP)</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label>Модель (необов'язково)</Label>
                <Input value={model} onChange={(e: any) => setModel(e.target.value)} placeholder="Cummins C275" />
              </div>
              <div className="space-y-2">
                <Label>Серійний номер (необов'язково)</Label>
                <Input value={serialNumber} onChange={(e: any) => setSerialNumber(e.target.value)} placeholder="SN49283742" />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Тип палива</Label>
                <select className={selectClassName} value={fuelType} onChange={(e: any) => setFuelType(e.target.value)}>
                  <option value="A92">Бензин А-92 (A92)</option>
                  <option value="A95">Бензин А-95 (A95)</option>
                  <option value="DIESEL">Дизель (DIESEL)</option>
                  <option value="GAS">Газ (GAS)</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label>Місткість баку (літри)</Label>
                <Input type="number" step="0.1" value={tankCapacity} onChange={(e: any) => setTankCapacity(e.target.value)} placeholder="0.0" />
              </div>
              <div className="space-y-2">
                <Label>Витрата палива (літри/год)</Label>
                <Input type="number" step="0.1" value={fuelConsumption} onChange={(e: any) => setFuelConsumption(e.target.value)} placeholder="15.5" />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Поточні (початкові) мотогодини</Label>
                <Input type="number" step="1" value={initialMotohours} onChange={(e: any) => setInitialMotohours(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Інтервал ТО (год)</Label>
                <Input type="number" step="1" value={maintenanceInterval} onChange={(e: any) => setMaintenanceInterval(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Попередження перед ТО (год)</Label>
                <Input type="number" step="1" value={toWarningBefore} onChange={(e: any) => setToWarningBefore(e.target.value)} />
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-between items-center mt-2">
          <Button variant="outline" onClick={handlePrev} disabled={step === 1 || loading}>
            Назад
          </Button>
          
          {step < 3 ? (
            <Button onClick={handleNext}>
              Далі
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {loading ? 'Створення...' : 'Створити'}
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
