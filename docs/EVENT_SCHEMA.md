# Event Log Schema

## EventType enum

Всі типи подій визначені в `app/core/event_types.py` (StrEnum).  
ЗАБОРОНЕНО використовувати рядкові літерали — тільки `EventType.SHIFT_STARTED` тощо.

| Значення | Коли викликається | Обов'язкові поля `meta` |
|----------|-------------------|-------------------------|
| `SHIFT_STARTED` | `ShiftService.start_shift()` | `shift_id`, `generator_id`, `operator_id` |
| `SHIFT_STOPPED` | `ShiftService.stop_shift()` | `shift_id`, `generator_id`, `motohours` |
| `FUEL_REFILL` | `FuelService.add_refill()` | `shift_id`, `generator_id`, `liters` |
| `FUEL_DELIVERY` | `FuelService.add_delivery()` | `delivery_id`, `liters`, `supplier` |

## Структура запису event_log

```python
await event_log.write(
    event_type=EventType.SHIFT_STARTED,
    meta={
        "shift_id": str(shift.id),
        "generator_id": str(generator_id),
        "operator_id": str(operator_id),
    },
    db=db  # та сама сесія, та сама транзакція
)
```

## Приклади meta

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
  "liters": "200.00",
  "supplier": "ТОВ Паливо"
}
```

> **Важливо:** `liters` та `motohours` передаються як рядки (str(Decimal)), щоб уникнути проблем із серіалізацією float у JSON.
