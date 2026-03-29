# System Invariants

> Цей файл — **обов'язковий до прочитання** перед реалізацією будь-якого сервісного методу.
> Порушення будь-якого інваріанту може призвести до розсинхрону даних або некоректної аналітики.

---

## Таблиця інваріантів

| # | Інваріант | Де enforced | Наслідок порушення |
|---|-----------|-------------|--------------------|
| 1 | **Тільки ONE active shift globally** | `RulesService.check_no_active_shift_exists()` | Race condition, подвійна витрата палива |
| 2 | **motohours рахується ТІЛЬКИ при stop** | `ShiftService.stop_shift()` | Неправильний облік ресурсу, фантомний ТО |
| 3 | **`fuel_stock.current_liters` — SOURCE OF TRUTH** | `FuelService`, atomic update | Розсинхрон залишку палива через 2–3 дні |
| 4 | **Кожна бізнес-операція — одна транзакція** | всі `*Service` методи | Неатомарний запис, часткові зміни у БД |
| 5 | **Кожна операція → event_log в тій самій транзакції** | `EventLogRepository` | Відсутній запис в журналі, аналітика неповна |
| 6 | **`EventType` — тільки через enum** | `app/common/event_types.py` | Різні рядки для одної події, зламана аналітика |

---

## Деталі критичних інваріантів

### Інваріант 1 — Одна активна зміна глобально

`ACTIVE` зміна — **завжди одна на весь проєкт**, не per-generator, не per-user.

Обґрунтування: один генератор може фізично працювати в один момент часу.

```python
# ПРАВИЛЬНА назва методу перевірки:
await rules.check_no_active_shift_exists(db)
# НЕ check_only_one_generator_active() — ця назва вводить в оману
```

### Інваріант 2 — Формула мотогодин

```python
from decimal import Decimal

# ЄДИНА канонічна формула:
hours = Decimal(
    str((stopped_at - started_at).total_seconds() / 3600)
).quantize(Decimal("0.01"))

# ❌ НЕ: (stopped_at - started_at).seconds / 3600  ← не враховує дні
# ❌ НЕ: float арифметика  ← втрата точності
```

> `stopped_at` записується в момент зупинки зміни. Не перераховується пізніше.

### Інваріант 3 — Джерело істини по паливу

`fuel_stock.current_liters` — **не кеш**, а актуальний залишок.
- `fuel_deliveries` та `fuel_refills` — аудит-лог, **не** джерело для розрахунку.
- Оновлюється **атомарно** при кожній операції з пальним всередині транзакції.

```python
# ✅ ПРАВИЛЬНО:
async with db.begin():
    stock = await fuel_repo.get_stock(db)
    stock.current_liters -= refill_liters  # атомарно
    await fuel_repo.create_refill(refill_data, db)
    await event_log.write(EventType.FUEL_REFILL, meta={...}, db=db)
```

### Інваріант 4+5 — Канонічний шаблон транзакції

Всі сервісні методи, що змінюють стан, повинні слідувати цьому шаблону:

```python
async def start_shift(generator_id: UUID, operator_id: UUID, db: AsyncSession) -> Shift:
    # 1. Read-only перевірки (поза транзакцією)
    await rules.check_no_active_shift_exists(db)
    await rules.check_min_pause_between_starts(generator_id, db)

    # 2. Всі мутації + event_log — в одній транзакції
    async with db.begin():
        shift = await shift_repo.create(generator_id, operator_id, db)
        await event_log.write(
            event_type=EventType.SHIFT_STARTED,
            meta={"shift_id": str(shift.id), "generator_id": str(generator_id)},
            db=db
        )

    # 3. Повернути результат (поза транзакцією)
    return shift
```

---

## Edge cases та відновлення

### Падіння сервера під час активної зміни

При старті застосунку (`lifespan`) перевіряти наявність `ACTIVE` змін старше `ORPHAN_SHIFT_THRESHOLD_HOURS` (default: 24 год).

- Якщо знайдено → логувати WARNING, не закривати автоматично.
- Адмін закриває вручну через `/api/shifts/{id}/force-close` (тільки `ADMIN`).

### `check_min_pause_between_starts` — scope

Перевірка **per-generator**: між зупинкою попередньої зміни для конкретного генератора і стартом нової.
Глобального обмеження немає — тільки per-generator.
Мінімальна пауза: `MIN_PAUSE_MINUTES` з `system_settings` (default: 15 хв).
