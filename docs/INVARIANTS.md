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
Один генератор може фізично працювати в один момент часу.  
Перевірка відбувається ДО початку транзакції (read-only).  
Назва методу `check_only_one_generator_active()` вводить в оману — правильна семантика: немає жодної активної зміни глобально.

### Інваріант 2 — motohours тільки при stop
Години НЕ рахуються динамічно. Вони записуються один раз у момент `stop_shift()`.  
Якщо сервер впав і зміна не закрита — потрібна ручна або автоматична recovery-процедура.

### Інваріант 3 — fuel_stock.current_liters як джерело істини
`fuel_stock.current_liters` оновлюється атомарно при кожній операції з пальним.  
`fuel_deliveries` і `fuel_refills` — аудит-лог, НЕ основа для розрахунку поточного залишку.

### Інваріант 4 та 5 — транзакції та event_log
Порядок операцій у будь-якому `*Service` методі:
```
1. Перевірки поза транзакцією (read-only)
2. async with db.begin():
   a. мутація даних
   b. event_log.write() — в тій же транзакції
3. Повернути результат
```
