# Event Log Schema

## EventType enum

Всі типи визначені в `app/core/event_types.py` (StrEnum).

| Значення | Коли | Обов'язкові поля `meta` |
|----------|------|------------------------|
| `SHIFT_STARTED` | `ShiftService.start_shift()` | `shift_id`, `generator_id`, `operator_id` |
| `SHIFT_STOPPED` | `ShiftService.stop_shift()` | `shift_id`, `generator_id`, `motohours` |
| `FUEL_REFILL` | `FuelService.add_refill()` | `shift_id`, `generator_id`, `liters` |
| `FUEL_DELIVERY` | `FuelService.add_delivery()` | `delivery_id`, `liters`, `supplier` |

## Структура запису

```json
{
  "event_type": "SHIFT_STARTED",
  "created_at": "2026-03-29T20:00:00Z",
  "meta": {
    "shift_id": "uuid",
    "generator_id": "uuid",
    "operator_id": "uuid"
  }
}
```

## Правила

- `event_log` завжди пишеться **в тій самій транзакції** що й основна операція
- Якщо `event_log` падає — вся транзакція відкочується
- `meta` — JSON, всі UUID передаються як рядки (`str(uuid)`)
- `liters` і `motohours` передаються як рядки Decimal (`"12.50"`), не float
