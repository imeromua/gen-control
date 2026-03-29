# System Invariants

| # | Інваріант | Де enforced |
|---|-----------|-------------|
| 1 | Тільки ONE active shift globally | `RulesService.check_no_active_shift_exists()` |
| 2 | motohours рахується ТІЛЬКИ при stop | `ShiftService.stop_shift()` |
| 3 | `fuel_stock.current_liters` — SOURCE OF TRUTH | `FuelService`, atomic update |
| 4 | Кожна бізнес-операція — одна транзакція | всі `*Service` методи |
| 5 | Кожна операція → event_log в тій же транзакції | `EventLogRepository` |
| 6 | motohours formula: `Decimal((stopped_at - started_at).total_seconds() / 3600).quantize("0.01")` | `ShiftService` |

## Пояснення критичних інваріантів

### Інваріант #1 — ONE active shift globally
Активна зміна може бути **тільки одна** в будь-який момент часу — незалежно від генератора чи оператора.
Фізичне обґрунтування: один майданчик, один генератор працює одночасно.

> ⚠️ `check_only_one_generator_active()` — застаріла назва. Використовувати `check_no_active_shift_exists()`.

### Інваріант #3 — fuel_stock.current_liters
`fuel_stock.current_liters` — не кеш, не розрахункове поле. Це **єдине джерело істини**.
`fuel_deliveries` та `fuel_refills` — аудит-лог, не основа розрахунку.

### Інваріант #4 + #5 — транзакція + event_log
Канонічний порядок операцій у кожному service-методі:
```python
# 1. Read-only перевірки (поза транзакцією)
await rules.check_...()

# 2. Мутації + event_log — ОДНА транзакція
async with db.begin():
    entity = await repo.create(...)
    await event_log.write(event_type=EventType.X, meta={...}, db=db)

# 3. Повернути результат
return entity
```
