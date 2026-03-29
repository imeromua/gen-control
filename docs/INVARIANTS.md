# System Invariants

| # | Інваріант | Де enforced |
|---|-----------|-------------|
| 1 | Тільки ONE active shift globally | `RulesService.check_no_active_shift_exists()` |
| 2 | motohours рахується ТІЛЬКИ при stop | `ShiftService.stop_shift()` |
| 3 | `fuel_stock.current_liters` — SOURCE OF TRUTH | `FuelService`, atomic update |
| 4 | Кожна бізнес-операція — одна транзакція | всі `*Service` методи |
| 5 | Кожна операція → event_log в тій же транзакції | `EventLogRepository` |
| 6 | motohours formula: `Decimal((stopped_at - started_at).total_seconds() / 3600).quantize("0.01")` | `ShiftService` |

## Пояснення

### Інваріант 1 — ONE active shift globally
Активна зміна завжди ОДНА — не per-generator, не per-user.  
Обґрунтування: один фізичний генератор може працювати в один момент часу.  
Перевіряється перед будь-яким `start_shift()`.

### Інваріант 2 — motohours тільки при stop
Мотогодини не рахуються "в реальному часі". Значення `motohours` записується
одноразово при виклику `stop_shift()` і більше не змінюється.

### Інваріант 3 — fuel_stock є джерелом правди
`fuel_stock.current_liters` — це не кеш і не агрегат.  
Це єдине джерело правди про залишок палива.  
`fuel_deliveries` і `fuel_refills` — аудит-лог, не основа розрахунку.

### Інваріант 4 — атомарність
Кожна операція яка змінює стан системи ОБОВ'ЯЗКОВО виконується в межах
однієї транзакції БД. Часткові зміни неприпустимі.

### Інваріант 5 — event_log в тій самій транзакції
Запис у `event_log` є частиною бізнес-операції, а не наступним кроком після.
Якщо event_log падає — вся транзакція відкочується.

### Інваріант 6 — формула motohours
```python
from decimal import Decimal

motohours = Decimal(
    str((stopped_at - started_at).total_seconds() / 3600)
).quantize(Decimal("0.01"))
```
Використовувати `Decimal`, НЕ `float`. Округлення — до 2 знаків.
