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
Активна зміна — завжди одна глобально, не per-generator і не per-user.
Обґрунтування: лише один генератор може фізично працювати в один момент часу.
Метод перевірки: `check_no_active_shift_exists()` (не `check_only_one_generator_active` — стара назва вводила в оману).

### Інваріант 3 — fuel_stock.current_liters є SOURCE OF TRUTH
`fuel_stock.current_liters` — не кеш і не розрахунок з deliveries - refills.
Це єдине джерело правди. `fuel_deliveries` і `fuel_refills` — аудит-лог, не основа розрахунку.
При будь-якій операції з пальним `current_liters` оновлюється атомарно в межах транзакції.

### Інваріант 6 — формула мотогодин
```python
from decimal import Decimal
hours = Decimal(str((stopped_at - started_at).total_seconds() / 3600)).quantize(Decimal("0.01"))
```
Використовувати `Decimal`, не `float`. Округлення до 2 знаків.
