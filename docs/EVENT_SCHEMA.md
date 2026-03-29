# Event Log Schema

## EventType enum

Всі типи подій визначені в `app/core/event_types.py` як `StrEnum`.
НІКОЛИ не використовуй рядкові літерали напряму — тільки `EventType.SHIFT_STARTED` тощо.

| Значення | Коли викликається | Обов'язкові поля `meta` |
|----------|-------------------|-------------------------|
| `SHIFT_STARTED` | `ShiftService.start_shift()` | `shift_id`, `generator_id`, `operator_id` |
| `SHIFT_STOPPED` | `ShiftService.stop_shift()` | `shift_id`, `generator_id`, `motohours` |
| `FUEL_REFILL` | `FuelService.add_refill()` | `shift_id`, `generator_id`, `liters` |
| `FUEL_DELIVERY` | `FuelService.add_delivery()` | `delivery_id`, `liters`, `supplier` |

## meta structure examples

```json
// SHIFT_STARTED
{
  "shift_id": "550e8400-e29b-41d4-a716-446655440000",
  "generator_id": "550e8400-e29b-41d4-a716-446655440001",
  "operator_id": "550e8400-e29b-41d4-a716-446655440002"
}

// SHIFT_STOPPED
{
  "shift_id": "550e8400-e29b-41d4-a716-446655440000",
  "generator_id": "550e8400-e29b-41d4-a716-446655440001",
  "motohours": "4.75"
}

// FUEL_REFILL
{
  "shift_id": "550e8400-e29b-41d4-a716-446655440000",
  "generator_id": "550e8400-e29b-41d4-a716-446655440001",
  "liters": "120.50"
}

// FUEL_DELIVERY
{
  "delivery_id": "550e8400-e29b-41d4-a716-446655440003",
  "liters": "500.00",
  "supplier": "Постачальник ТОВ"
}
```

## Rules

- `liters` та `motohours` — завжди рядок (серіалізований `Decimal`), НЕ float
- UUID — завжди рядок (`str(uuid)`)
- `meta` — обов'язковий для кожного запису, порожній dict заборонений
