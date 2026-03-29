# Event Log Schema

## EventType enum

Всі типи визначені в `app/core/event_types.py` як `StrEnum`.

| Значення | Коли | Обов'язкові поля meta |
|----------|------|----------------------|
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
  "motohours": "4.25"
}

// FUEL_REFILL
{
  "shift_id": "550e8400-e29b-41d4-a716-446655440000",
  "generator_id": "550e8400-e29b-41d4-a716-446655440001",
  "liters": "50.00"
}

// FUEL_DELIVERY
{
  "delivery_id": "550e8400-e29b-41d4-a716-446655440003",
  "liters": "200.00",
  "supplier": "OKKO"
}
```

## Правила

- `event_type` **завжди** береться з `EventType` enum — не рядкові літерали
- `meta` — `dict`, всі числа як `str` (Decimal serialized)
- `event_log` пишеться **в тій самій транзакції** що й основна мутація
