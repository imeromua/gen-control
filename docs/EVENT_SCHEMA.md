# Event Log Schema

## EventType enum

Всі значення визначені в `app/core/event_types.py` як `StrEnum`.

| Значення | Коли генерується | Обов'язкові поля `meta` |
|----------|-----------------|------------------------|
| `SHIFT_STARTED` | `ShiftService.start_shift()` | `shift_id`, `generator_id`, `operator_id` |
| `SHIFT_STOPPED` | `ShiftService.stop_shift()` | `shift_id`, `generator_id`, `motohours` |
| `FUEL_REFILL` | `FuelService.add_refill()` | `shift_id`, `generator_id`, `liters` |
| `FUEL_DELIVERY` | `FuelService.add_delivery()` | `delivery_id`, `liters`, `supplier` |

## Структура запису event_log

```json
{
  "event_type": "SHIFT_STARTED",
  "created_at": "2026-03-29T21:00:00Z",
  "meta": {
    "shift_id": "550e8400-e29b-41d4-a716-446655440000",
    "generator_id": "550e8400-e29b-41d4-a716-446655440001",
    "operator_id": "550e8400-e29b-41d4-a716-446655440002"
  }
}
```

## Правила

- `event_type` — завжди з enum `EventType`, ніколи рядок-літерал
- `liters` у `meta` — рядок у форматі Decimal (`"12.50"`, не `12.5`)
- `motohours` у `meta` — рядок у форматі Decimal (`"3.25"`, не `3.25`)
- Запис у `event_log` виконується в межах **тієї ж транзакції**, що й основна операція
