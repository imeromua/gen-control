# System Invariants

| # | Інваріант | Де enforced |
|---|-----------|-------------|
| 1 | Тільки ONE active shift globally | `RulesService.check_no_active_shift_exists()` |
| 2 | motohours рахується ТІЛЬКИ при stop | `ShiftService.stop_shift()` |
| 3 | `fuel_stock.current_liters` — SOURCE OF TRUTH | `FuelService`, atomic update |
| 4 | Кожна бізнес-операція — одна транзакція | всі `*Service` методи |
| 5 | Кожна операція → event_log в тій же транзакції | `EventLogRepository` |
| 6 | motohours formula: `Decimal((stopped_at - started_at).total_seconds() / 3600).quantize("0.01")` | `ShiftService` |

---

## Explicit Operation Flow

> Порядок операцій всередині кожного service-методу є фіксованим і не підлягає зміні.
> Порушення порядку може призвести до race condition або порушення консистентності.

### start_shift()

```python
async with db.begin():                                      # 1. відкрити транзакцію
    await rules.check_no_active_shift_exists()              # 2. глобальний інваріант: немає активного шифту
    await rules.check_min_pause_between_starts(generator_id) # 3. перевірка паузи для цього генератора
    shift = await shift_repo.create(...)                    # 4. створити запис shift зі статусом ACTIVE
    await event_log_repo.create(                            # 5. event_log — в тій же транзакції
        event_type=EventType.SHIFT_STARTED,
        meta={"shift_id": shift.id, "generator_id": ..., "operator_id": ...}
    )
# commit відбувається автоматично при виході з блоку
```

### stop_shift()

```python
async with db.begin():                                      # 1. відкрити транзакцію
    shift = await shift_repo.get_active_or_raise()          # 2. отримати активний шифт (або 404)
    motohours = Decimal(                                    # 3. розрахувати мотогодини
        (stopped_at - shift.started_at).total_seconds() / 3600
    ).quantize(Decimal("0.01"))
    await shift_repo.update(shift, status=CLOSED,           # 4. оновити запис
                            stopped_at=stopped_at,
                            motohours=motohours)
    await event_log_repo.create(                            # 5. event_log — в тій же транзакції
        event_type=EventType.SHIFT_STOPPED,
        meta={"shift_id": shift.id, "generator_id": ..., "motohours": str(motohours)}
    )
# commit відбувається автоматично при виході з блоку
```

### add_refill()

```python
async with db.begin():                                      # 1. відкрити транзакцію
    shift = await shift_repo.get_active_or_raise()          # 2. активний шифт обов'язковий
    await fuel_repo.create_refill(...)                      # 3. створити запис refill
    await fuel_stock_repo.decrement(liters)                 # 4. зменшити fuel_stock.current_liters (SOURCE OF TRUTH)
    await event_log_repo.create(                            # 5. event_log — в тій же транзакції
        event_type=EventType.FUEL_REFILL,
        meta={"shift_id": shift.id, "generator_id": ..., "liters": str(liters)}
    )
```

### add_delivery()

```python
async with db.begin():                                      # 1. відкрити транзакцію
    delivery = await fuel_repo.create_delivery(...)         # 2. створити запис delivery
    await fuel_stock_repo.increment(liters)                 # 3. збільшити fuel_stock.current_liters (SOURCE OF TRUTH)
    await event_log_repo.create(                            # 4. event_log — в тій же транзакції
        event_type=EventType.FUEL_DELIVERY,
        meta={"delivery_id": delivery.id, "liters": str(liters), "supplier": ...}
    )
```

---

## Edge Cases

| Ситуація | Поведінка |
|---|---|
| Сервер впав під час активного шифту | shift лишається ACTIVE; при перезапуску — адмін закриває вручну через `force_stop` endpoint |
| `add_refill` без активного шифту | `ShiftNotFoundError` (HTTP 409) |
| Два одночасні `start_shift` | DB-level lock через `SELECT FOR UPDATE` в `check_no_active_shift_exists()` |
| `fuel_stock.current_liters` < 0 | `FuelService` перевіряє перед декрементом, кидає `InsufficientFuelError` |
