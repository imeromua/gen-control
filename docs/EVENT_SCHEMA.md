# Event Log Schema

## EventType enum

| Значення | Коли | Обов'язкові поля meta |
|----------|------|----------------------|
| SHIFT_STARTED | start_shift() | shift_id, generator_id, operator_id |
| SHIFT_STOPPED | stop_shift() | shift_id, generator_id, motohours |
| FUEL_REFILL | add_refill() | shift_id, generator_id, liters |
| FUEL_DELIVERY | add_delivery() | delivery_id, liters, supplier |

## meta structure example

```json
{
  "shift_id": "uuid",
  "generator_id": "uuid",
  "liters": "12.50"
}
```
