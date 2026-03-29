# System Invariants

| # | Інваріант | Де enforced |
|---|-----------|-------------|
| 1 | Тільки ONE active shift globally | `RulesService.check_no_active_shift_exists()` |
| 2 | motohours рахується ТІЛЬКИ при stop | `ShiftService.stop_shift()` |
| 3 | `fuel_stock.current_liters` — SOURCE OF TRUTH | `FuelService`, atomic update |
| 4 | Кожна бізнес-операція — одна транзакція | всі `*Service` методи |
| 5 | Кожна операція → event_log в тій же транзакції | `EventLogRepository` |
| 6 | motohours formula: `Decimal((stopped_at - started_at).total_seconds() / 3600).quantize("0.01")` | `ShiftService` |

## Порядок операцій у сервісах

```python
# Канонічний шаблон для будь-якого *Service методу:

# 1. Read-only перевірки (поза транзакцією)
await rules.check_...(db)

# 2. Мутації — одна транзакція
async with db.begin():
    entity = await repo.create(..., db)
    await event_log.write(event_type=EventType.X, meta={...}, db=db)

# 3. Повернути результат
return entity
```

## Інваріант Active Shift

- `ACTIVE` зміна — завжди **одна глобально** (не per-generator, не per-user)
- Обґрунтування: один фізичний генератор може працювати в один момент часу
- `check_no_active_shift_exists()` — перевіряє глобально

## Відновлення після падіння сервера

- При старті застосунку: шукати `ACTIVE` зміни старше N годин
- Дія: алертити адміна або закривати автоматично (визначити в конфігурації)
