# Event Log Schema

> Всі записи в `event_log` **обов'язково** використовують `EventType` enum з `app/common/event_types.py`.
> Ніколи не передавати рядки напряму — тільки через enum.

---

## EventType — повний список

| `event_type` | Коли створюється | Ініціатор |
|---|---|---|
| `SHIFT_STARTED` | `ShiftService.start_shift()` | ADMIN / OPERATOR |
| `SHIFT_STOPPED` | `ShiftService.stop_shift()` | ADMIN / OPERATOR |
| `FUEL_REFILL` | `FuelService.add_refill()` | ADMIN / OPERATOR |
| `FUEL_DELIVERY` | `FuelService.add_delivery()` | ADMIN / OPERATOR |
| `OIL_ADDED` | `OilService.add_oil()` | ADMIN / OPERATOR |
| `ADJUSTMENT` | `AdjustmentService.create()` | тільки ADMIN |
| `OUTAGE_CREATED` | `OutageService.create()` | ADMIN / OPERATOR |
| `OUTAGE_UPDATED` | `OutageService.update()` | ADMIN / OPERATOR |

---

## Структура `meta` по типах подій

### `SHIFT_STARTED`
```json
{
  "shift_id": "uuid",
  "generator_id": "uuid",
  "operator_id": "uuid"
}
```

### `SHIFT_STOPPED`
```json
{
  "shift_id": "uuid",
  "generator_id": "uuid",
  "operator_id": "uuid",
  "motohours": "1.75",
  "fuel_consumed_liters": "12.50"
}
```

### `FUEL_REFILL`
```json
{
  "shift_id": "uuid",
  "generator_id": "uuid",
  "liters": "20.00",
  "stock_after": "85.50"
}
```

### `FUEL_DELIVERY`
```json
{
  "delivery_id": "uuid",
  "liters": "100.00",
  "supplier": "string або null",
  "stock_after": "185.50"
}
```

### `OIL_ADDED`
```json
{
  "generator_id": "uuid",
  "liters": "2.00",
  "stock_after": "8.00"
}
```

### `ADJUSTMENT`
```json
{
  "field": "fuel_stock.current_liters",
  "old_value": "85.50",
  "new_value": "90.00",
  "reason": "string"
}
```

### `OUTAGE_CREATED` / `OUTAGE_UPDATED`
```json
{
  "outage_id": "uuid",
  "scheduled_start": "2026-03-29T07:00:00",
  "scheduled_end": "2026-03-29T12:00:00"
}
```

---

## Правила запису

1. `meta` — завжди `dict[str, str]` (всі числа як рядки, всі UUID як рядки)
2. Запис event_log — **в тій самій транзакції**, що й основна операція
3. При відкаті транзакції event_log також відкочується автоматично
4. `event_log` — **read-only** для всіх ролей через API (тільки GET)

---

## Приклад виклику

```python
from app.common.event_types import EventType

await event_log.write(
    event_type=EventType.SHIFT_STARTED,
    meta={
        "shift_id": str(shift.id),
        "generator_id": str(generator_id),
        "operator_id": str(operator_id),
    },
    db=db,  # та ж сесія, що й основна операція
)
```
