# Frontend Error Handling — Глобальна обробка помилок

## Архітектура

```
API помилка
    → lib/api.ts (перехоплює і кидає ApiError)
    → hooks/* (ловить і передає error в state)
    → components (відображують toast або inline error)
```

---

## 1. `lib/api.ts` — центральний API клієнт

```typescript
export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail)
    this.name = 'ApiError'
  }
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const token = getToken()  // з cookie або localStorage
  
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: 'Невідома помилка' }))
    
    // Спеціальна обробка 401 — авто редирект на /login
    if (res.status === 401) {
      clearToken()
      window.location.href = '/login'
    }
    
    throw new ApiError(res.status, body.detail ?? 'Невідома помилка')
  }

  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  get:    <T>(url: string) => request<T>(url),
  post:   <T>(url: string, body: unknown) => request<T>(url, { method: 'POST', body: JSON.stringify(body) }),
  put:    <T>(url: string, body: unknown) => request<T>(url, { method: 'PUT', body: JSON.stringify(body) }),
  patch:  <T>(url: string, body: unknown) => request<T>(url, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(url: string) => request<T>(url, { method: 'DELETE' }),
}
```

---

## 2. Матриця обробки помилок

| HTTP | Ситуація | Фронтенд поведінка |
|---|---|---|
| 400 | Невірні дані | 🟡 toast: текст з `detail` |
| 401 | Не авторизовано | 🔄 авто redirect на `/login` |
| 403 | Заборонено правилами | 🟠 toast: `"Операція заборонена: " + detail` |
| 404 | Не знайдено | 🟡 toast: `"Не знайдено"` |
| 409 | Конфлікт стану | 🟠 toast: `detail` (завжди описовий) |
| 422 | Помилка валідації | 🟡 toast: поль з помилкою |
| 500 | Серверна помилка | 🔴 toast: `"Помилка сервера, спробуйте пізніше"` |
| Network | Сервер недоступний | 🔴 toast: `"Немає з'єднання з сервером"` |

---

## 3. Хук `useApiAction` — для мутацій

Використовуй для всіх POST/PUT/DELETE операцій (старт, стоп, доставка тощо):

```typescript
// hooks/useApiAction.ts
import { useState, useCallback } from 'react'
import { ApiError } from '@/lib/api'
import { useToast } from '@/hooks/useToast'

export function useApiAction<T>(
  action: () => Promise<T>,
  options?: {
    onSuccess?: (data: T) => void
    successMessage?: string
  }
) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  const execute = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await action()
      if (options?.successMessage) {
        toast({ title: options.successMessage, variant: 'success' })
      }
      options?.onSuccess?.(data)
      return data
    } catch (err) {
      const message = err instanceof ApiError
        ? err.detail
        : 'Невідома помилка'
      setError(message)
      toast({ title: message, variant: getToastVariant(err) })
    } finally {
      setLoading(false)
    }
  }, [action])

  return { execute, loading, error }
}

function getToastVariant(err: unknown): 'warning' | 'error' {
  if (err instanceof ApiError && (err.status === 409 || err.status === 403)) {
    return 'warning'
  }
  return 'error'
}
```

### Використання в компоненті:

```typescript
// Замість бойлерплейту try/catch в кожному компоненті:
const { execute: startShift, loading } = useApiAction(
  () => api.post('/api/shifts/start', { generator_id: genId }),
  {
    successMessage: 'Зміну запущено',
    onSuccess: () => router.refresh()
  }
)

<Button onClick={startShift} disabled={loading}>
  {loading ? 'Запуск...' : 'Запустити генератор'}
</Button>
```

---

## 4. SWR polling — обробка помилок

```typescript
// hooks/useDashboard.ts
import useSWR from 'swr'
import { api, ApiError } from '@/lib/api'

export function useDashboard() {
  const { data, error, isLoading } = useSWR(
    '/api/dashboard/summary',
    () => api.get('/api/dashboard/summary'),
    {
      refreshInterval: 30_000,
      onError: (err) => {
        // Поллінг не спамить toast при кожній помилці
        // Тільки відображаємо offline банер при network error
        if (!(err instanceof ApiError)) {
          setOffline(true)
        }
      }
    }
  )

  return {
    dashboard: data,
    isLoading,
    isError: !!error,
    isOffline: error && !(error instanceof ApiError)
  }
}
```

---

## 5. Offline банер

На всіх сторінках показувати повідомлення коли сервер недоступний:

```typescript
// components/layout/OfflineBanner.tsx
import { useEffect, useState } from 'react'

export function OfflineBanner() {
  const [offline, setOffline] = useState(false)

  useEffect(() => {
    const on = () => setOffline(true)
    const off = () => setOffline(false)
    window.addEventListener('offline', on)
    window.addEventListener('online', off)
    return () => {
      window.removeEventListener('offline', on)
      window.removeEventListener('online', off)
    }
  }, [])

  if (!offline) return null

  return (
    <div className="fixed top-0 inset-x-0 z-50 bg-red-600 text-white text-center py-2 text-sm">
      ⚠️ Немає з'єднання з сервером. Дані можуть бути неактуальними.
    </div>
  )
}
```

Додати в `app/layout.tsx`:
```tsx
import { OfflineBanner } from '@/components/layout/OfflineBanner'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <OfflineBanner />
        {children}
      </body>
    </html>
  )
}
```

---

## 6. Error Boundary (React)

Для помилок рендеру — не даємо білому екрану:

```typescript
// app/error.tsx (Next.js App Router вбудований Error Boundary)
'use client'

export default function ErrorPage({
  error,
  reset
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <h2 className="text-xl font-semibold">Щось пішло не так</h2>
      <p className="text-muted-foreground">{error.message}</p>
      <Button onClick={reset}>Спробувати знову</Button>
    </div>
  )
}
```

---

## Чек-ліст для агента

- [ ] `lib/api.ts` містить `ApiError` клас з `status` та `detail`
- [ ] HTTP 401 → авто redirect на `/login`
- [ ] Всі мутації через `useApiAction` (не сирий try/catch)
- [ ] SWR polling не спамить toast безперервно
- [ ] `OfflineBanner` в `layout.tsx`
- [ ] `app/error.tsx` — Error Boundary для Next.js
- [ ] 409/403 — `warning` variant toast, не `error`
