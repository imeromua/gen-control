# Event Log Schema

## EventType enum

Визначено в `app/core/event_types.py`. Завжди використовувати enum — ніколи рядкові літерали напряму.

| Значення | Коли викликається | Обов'язкові поля meta |
|----------|-------------------|----------------------|
| `SHIFT_STARTED` | `ShiftService.start_shift()` | `shift_id`, `generator_id`, `operator_id` |
| `SHIFT_STOPPED` | `ShiftService.stop_shift()` | `shift_id`, `generator_id`, `motohours` |
| `FUEL_REFILL` | `FuelService.add_refill()` | `shift_id`, `generator_id`, `liters` |
| `FUEL_DELIVERY` | `FuelService.add_delivery()` | `delivery_id`, `liters`, `supplier` |

## meta structure

```json
// SHIFT_STARTED / SHIFT_STOPPED
{
  "shift_id": "uuid-string",
  "generator_id": "uuid-string",
  "operator_id": "uuid-string",
  "motohours": "12.50"
}

// FUEL_REFILL
{
  "shift_id": "uuid-string",
  "generator_id": "uuid-string",
  "liters": "50.00"
}

// FUEL_DELIVERY
{
  "delivery_id": "uuid-string",
  "liters": "200.00",
  "supplier": "string"
}
```

## Правила

- `meta` — завжди `dict`, значення серіалізовані в рядки (`str(uuid)`, `str(decimal)`)
- event_log пишеться **в тій самій транзакції** що й основна мутація
- Якщо event_log падає — вся транзакція відкочується
