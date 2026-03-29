# System Invariants

| # | Інваріант | Де enforced |
|---|-----------|-------------|
| 1 | Тільки ONE active shift globally | `RulesService.check_no_active_shift_exists()` |
| 2 | motohours рахується ТІЛЬКИ при stop | `ShiftService.stop_shift()` |
| 3 | `fuel_stock.current_liters` — SOURCE OF TRUTH | `FuelService`, atomic update |
| 4 | Кожна бізнес-операція — одна транзакція | всі `*Service` методи |
| 5 | Кожна операція → event_log в тій же транзакції | `EventLogRepository` |
| 6 | motohours formula: `Decimal((stopped_at - started_at).total_seconds() / 3600).quantize("0.01")` | `ShiftService` |

## Canonical transaction pattern

```python
async def start_shift(generator_id: UUID, operator_id: UUID, db: AsyncSession) -> Shift:
    # 1. Перевірки поза транзакцією (read-only)
    await rules.check_no_active_shift_exists(db)
    await rules.check_min_pause_between_starts(generator_id, db)

    # 2. Мутації — все в одній транзакції
    async with db.begin():
        shift = await shift_repo.create(generator_id, operator_id, db)
        await event_log.write(
            event_type=EventType.SHIFT_STARTED,
            meta={"shift_id": str(shift.id), "generator_id": str(generator_id)},
            db=db
        )
    return shift
```

## Примітки

- `check_only_one_generator_active()` перейменовано на `check_no_active_shift_exists()` — інваріант глобальний, не per-generator
- При старті застосунку: ACTIVE-зміни старші N годин → алерт адміну або автозакриття (background task)
