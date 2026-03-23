'use client';
import { useState, useEffect } from 'react';

interface Toast {
  id: string;
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive';
}

const toastState: { toasts: Toast[]; listeners: (() => void)[] } = {
  toasts: [],
  listeners: [],
};

function notify() {
  toastState.listeners.forEach((l) => l());
}

export function toast(t: Omit<Toast, 'id'>) {
  const id = Math.random().toString(36).slice(2);
  toastState.toasts = [...toastState.toasts, { ...t, id }];
  notify();
  setTimeout(() => {
    toastState.toasts = toastState.toasts.filter((x) => x.id !== id);
    notify();
  }, 4000);
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>(toastState.toasts);

  useEffect(() => {
    const listener = () => setToasts([...toastState.toasts]);
    toastState.listeners.push(listener);
    return () => {
      toastState.listeners = toastState.listeners.filter((l) => l !== listener);
    };
  }, []);

  return { toasts };
}
