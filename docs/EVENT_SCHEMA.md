# Event Log Schema

## EventType enum

Використовувати тільки значення з `app/core/event_types.py` (StrEnum). Рядкові літерали заборонені.

| Значення | Коли | Обов'язкові поля `meta` |
|----------|------|--------------------------|
| `SHIFT_STARTED` | `ShiftService.start_shift()` | `shift_id`, `generator_id`, `operator_id` |
| `SHIFT_STOPPED` | `ShiftService.stop_shift()` | `shift_id`, `generator_id`, `motohours` |
| `FUEL_REFILL` | `FuelService.add_refill()` | `shift_id`, `generator_id`, `liters` |
| `FUEL_DELIVERY` | `FuelService.add_delivery()` | `delivery_id`, `liters`, `supplier` |

## meta structure

```json
{
  "shift_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "generator_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "operator_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

```json
{
  "shift_id": "uuid",
  "generator_id": "uuid",
  "motohours": "12.50"
}
```

```json
{
  "shift_id": "uuid",
  "generator_id": "uuid",
  "liters": "85.00"
}
```

## Правила

- `meta` — завжди `dict[str, str]`, Decimal/UUID серіалізуються як рядки
- event_log пишеться **в тій самій транзакції** що і основна мутація
- якщо event_log падає — вся транзакція відкочується (консистентність гарантована)
