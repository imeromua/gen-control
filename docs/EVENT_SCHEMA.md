# Event Log Schema

## EventType enum

Використовуй **тільки** значення з `app/core/event_types.py`. Ніяких рядкових літералів.

| Значення | Коли викликається | Обов'язкові поля `meta` |
|----------|-------------------|-------------------------|
| `SHIFT_STARTED` | `ShiftService.start_shift()` | `shift_id`, `generator_id`, `operator_id` |
| `SHIFT_STOPPED` | `ShiftService.stop_shift()` | `shift_id`, `generator_id`, `motohours` |
| `FUEL_REFILL` | `FuelService.add_refill()` | `shift_id`, `generator_id`, `liters` |
| `FUEL_DELIVERY` | `FuelService.add_delivery()` | `delivery_id`, `liters`, `supplier` |

## meta структура — приклади

### SHIFT_STARTED
```json
{
  "shift_id": "550e8400-e29b-41d4-a716-446655440000",
  "generator_id": "550e8400-e29b-41d4-a716-446655440001",
  "operator_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

### SHIFT_STOPPED
```json
{
  "shift_id": "550e8400-e29b-41d4-a716-446655440000",
  "generator_id": "550e8400-e29b-41d4-a716-446655440001",
  "motohours": "4.25"
}
```

### FUEL_REFILL
```json
{
  "shift_id": "550e8400-e29b-41d4-a716-446655440000",
  "generator_id": "550e8400-e29b-41d4-a716-446655440001",
  "liters": "50.00"
}
```

### FUEL_DELIVERY
```json
{
  "delivery_id": "550e8400-e29b-41d4-a716-446655440003",
  "liters": "500.00",
  "supplier": "OKKO"
}
```

## Правила
- `motohours` та `liters` — завжди рядок (Decimal serialized as string)
- Всі `*_id` — UUID у форматі рядка
- Додаткові поля дозволені, але обов'язкові — завжди присутні
