# Payload Examples — Приклади JSON запитів та відповідей

`Authorization: Bearer <token>` — рест ендпоінтів окрім публічних.

---

## Auth

### POST `/auth/login`
```json
// Request
{
  "username": "admin",
  "password": "mysecretpassword"
}

// Response 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

// Response 401
{
  "detail": "Невірний логін або пароль"
}
```

---

## Users

### POST `/users`
```json
// Request
{
  "full_name": "Іваненко Петро",
  "username": "petro_ivanen",
  "password": "securepass123",
  "role": "OPERATOR"
}

// Response 201
{
  "id": "a1b2c3d4-...",
  "full_name": "Іваненко Петро",
  "username": "petro_ivanen",
  "role": "OPERATOR",
  "is_active": true,
  "created_at": "2026-03-29T20:00:00Z"
}
```

---

## Generators

### POST `/api/generators`
```json
// Request
{
  "name": "Генератор #1",
  "model": "Honda EU70is"
}

// Response 201
{
  "id": "b2c3d4e5-...",
  "name": "Генератор #1",
  "model": "Honda EU70is",
  "is_active": true,
  "created_at": "2026-03-29T20:01:00Z"
}
```

### PUT `/api/generators/{id}/settings`
```json
// Request
{
  "fuel_type": "A95",
  "tank_capacity_liters": 25.0,
  "fuel_consumption_per_hour": 2.5,
  "to_interval_hours": 250.0,
  "to_warning_before_hours": 10.0
}

// Response 200
{
  "id": "c3d4e5f6-...",
  "generator_id": "b2c3d4e5-...",
  "fuel_type": "A95",
  "tank_capacity_liters": "25.00",
  "fuel_consumption_per_hour": "2.500",
  "to_interval_hours": "250.0",
  "to_warning_before_hours": "10.0",
  "updated_at": "2026-03-29T20:05:00Z"
}
```

---

## Shifts

### POST `/api/shifts/start`
```json
// Request
{
  "generator_id": "b2c3d4e5-..."
}

// Response 201
{
  "id": "d4e5f6a7-...",
  "shift_number": 42,
  "generator_id": "b2c3d4e5-...",
  "started_by": "a1b2c3d4-...",
  "started_at": "2026-03-29T20:10:00Z",
  "stopped_by": null,
  "stopped_at": null,
  "duration_minutes": null,
  "fuel_consumed_liters": null,
  "motohours_accumulated": null,
  "status": "ACTIVE"
}

// Response 409 — вже є активна зміна
{
  "detail": "Неможливо запустити: вже є активна зміна #41"
}

// Response 403 — поза робочим часом
{
  "detail": "Операції дозволені тільки в робочий час (07:00–22:00)"
}
```

### POST `/api/shifts/{id}/stop`
```json
// Request: тіло не потрібне

// Response 200
{
  "id": "d4e5f6a7-...",
  "shift_number": 42,
  "generator_id": "b2c3d4e5-...",
  "started_by": "a1b2c3d4-...",
  "started_at": "2026-03-29T20:10:00Z",
  "stopped_by": "a1b2c3d4-...",
  "stopped_at": "2026-03-29T22:15:00Z",
  "duration_minutes": "125.00",
  "fuel_consumed_liters": "5.208",
  "motohours_accumulated": "2.08",
  "status": "CLOSED"
}
```

---

## Fuel

### POST `/api/fuel/deliveries` — прийняти паливо
```json
// Request
{
  "liters": 50.0,
  "check_number": "Накладна-0042",
  "delivered_by_name": "Товарний Петров Антон"
}

// Response 201
{
  "id": "e5f6a7b8-...",
  "fuel_type": "A95",
  "liters": "50.00",
  "check_number": "Накладна-0042",
  "delivered_by_name": "Товарний Петров Антон",
  "accepted_by": "a1b2c3d4-...",
  "stock_before": "12.50",
  "stock_after": "62.50",
  "delivered_at": "2026-03-29T20:30:00Z"
}

// Response 409 — перевищення ліміту
{
  "detail": "Перевищення ліміту складу. Макс 200л, зараз 62.5л + 50л = 112.5л"
}
```

### POST `/api/fuel/refills` — заправити генератор
```json
// Request
{
  "generator_id": "b2c3d4e5-...",
  "liters": 10.0,
  "tank_level_before": 5.0
}

// Response 201
{
  "id": "f6a7b8c9-...",
  "generator_id": "b2c3d4e5-...",
  "performed_by": "a1b2c3d4-...",
  "liters": "10.00",
  "tank_level_before": "5.00",
  "tank_level_after": "15.00",
  "stock_before": "62.50",
  "stock_after": "52.50",
  "refilled_at": "2026-03-29T20:35:00Z"
}

// Response 409 — заправка під час роботи
{
  "detail": "Заправка під час активної зміни заборонена"
}
```

### GET `/api/fuel/stock`
```json
// Response 200
{
  "id": "g7h8i9j0-...",
  "fuel_type": "A95",
  "current_liters": "52.50",
  "max_limit_liters": "200.00",
  "warning_level_liters": "30.00",
  "updated_at": "2026-03-29T20:35:00Z"
}
```

---

## Dashboard

### GET `/api/dashboard/summary`
```json
// Response 200
{
  "active_shift": {
    "id": "d4e5f6a7-...",
    "shift_number": 42,
    "generator_name": "Генератор #1",
    "started_at": "2026-03-29T20:10:00Z",
    "started_by_name": "Іваненко Петро"
  },
  "fuel_stock": {
    "current_liters": "52.50",
    "max_limit_liters": "200.00",
    "warning_active": false,
    "critical_active": false
  },
  "motohours_today": "2.08",
  "next_outage": {
    "outage_date": "2026-03-30",
    "hour_start": 10,
    "hour_end": 14,
    "note": "Заплановане відключення"
  },
  "to_warning": {
    "active": false,
    "hours_remaining": "47.9"
  }
}
```

---

## Структура помилок

Всі помилки повертають структуру:
```json
{
  "detail": "Текст помилки українською"
}
```

| HTTP код | Ситуація |
|---|---|
| 200 | Успішне оновлення |
| 201 | Успішне створення |
| 400 | Невірні дані |
| 401 | Не авторизовано |
| 403 | Недостатньо прав |
| 404 | Не знайдено |
| 409 | Конфлікт стану |
| 422 | Помилка валідації Pydantic |
| 500 | Серверна помилка |
