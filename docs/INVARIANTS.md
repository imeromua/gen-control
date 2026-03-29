# System Invariants

| # | Інваріант | Де enforced |
|---|-----------|-------------|
| 1 | Тільки ONE active shift globally | `RulesService.check_no_active_shift_exists()` |
| 2 | motohours рахується ТІЛЬКИ при stop | `ShiftService.stop_shift()` |
| 3 | `fuel_stock.current_liters` — SOURCE OF TRUTH | `FuelService`, atomic update |
| 4 | Кожна бізнес-операція — одна транзакція | всі `*Service` методи |
| 5 | Кожна операція → event_log в тій же транзакції | `EventLogRepository` |
| 6 | motohours formula: `Decimal((stopped_at - started_at).total_seconds() / 3600).quantize("0.01")` | `ShiftService` |
