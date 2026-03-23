'use client';
import { useToast } from '@/hooks/useToast';
import { cn } from '@/lib/utils';

export function Toaster() {
  const { toasts } = useToast();

  return (
    <div className="fixed bottom-20 right-4 z-[100] flex flex-col gap-2 lg:bottom-4">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            'rounded-lg border px-4 py-3 shadow-lg text-sm max-w-xs transition-all',
            toast.variant === 'destructive'
              ? 'border-destructive bg-destructive text-destructive-foreground'
              : 'bg-background text-foreground'
          )}
        >
          {toast.title && <div className="font-semibold">{toast.title}</div>}
          {toast.description && <div className="opacity-80">{toast.description}</div>}
        </div>
      ))}
    </div>
  );
}
