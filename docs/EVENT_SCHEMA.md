# Event Log Schema

## EventType enum

Всі типи подій визначені в `app/core/event_types.py` як `StrEnum`.
ЗАБОРОНЕНО використовувати рядкові літерали напряму — тільки через `EventType.*`.

| Значення | Коли створюється | Хто створює |
|----------|-----------------|-------------|
| `SHIFT_STARTED` | при виклику `start_shift()` | `ShiftService` |
| `SHIFT_STOPPED` | при виклику `stop_shift()` | `ShiftService` |
| `FUEL_REFILL` | при виклику `add_refill()` | `FuelService` |
| `FUEL_DELIVERY` | при виклику `add_delivery()` | `FuelService` |

## Обов'язкові поля meta

### SHIFT_STARTED
```json
{
  "shift_id": "uuid",
  "generator_id": "uuid",
  "operator_id": "uuid"
}
```

### SHIFT_STOPPED
```json
{
  "shift_id": "uuid",
  "generator_id": "uuid",
  "motohours": "2.75"
}
```

### FUEL_REFILL
```json
{
  "shift_id": "uuid",
  "generator_id": "uuid",
  "liters": "50.00"
}
```

### FUEL_DELIVERY
```json
{
  "delivery_id": "uuid",
  "liters": "200.00",
  "supplier": "string"
}
```

## Правила

- `meta` зберігається як `JSONB`
- Числові значення (liters, motohours) — у форматі рядка з 2 знаками після коми
- UUID — у форматі рядка без дужок
- event_log записується в тій САМІЙ транзакції що і основна операція (див. INVARIANTS.md)
