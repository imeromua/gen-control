# Business Rules — Бізнес-логіка GenControl

Ці правила реалізовані в `RulesService` та окремих сервісах.
Порушення будь-якого правила → відповідна HTTP помилка.

## Зміни (Shifts)

### Запуск генератора
1. **Робочий час** — старт дозволено тільки між `system_settings.work_time_start` та `work_time_end` (Europe/Kyiv)
2. **Один генератор** — одночасно може працювати тільки ОДИН генератор. Якщо інший активний → HTTP 409
3. **Немає активної зміни** — у цього генератора не повинно бути відкритої зміни → HTTP 409
4. **Мінімальна пауза** — між зупинкою і новим запуском мінімум 30 хвилин → HTTP 409
5. **Генератор активний** — `generator.is_active = True` → HTTP 404/409

### Зупинка генератора
1. **Зміна існує** — можна зупинити тільки існуючу ACTIVE зміну → HTTP 404
2. **Права** — OPERATOR може зупинити тільки СВОЮ зміну (`started_by == current_user.id`). ADMIN може зупинити будь-яку
3. **При зупинці автоматично:**
   - Розраховується `duration_minutes = (stopped_at - started_at).total_seconds() / 60`
   - Розраховується `fuel_consumed_liters = duration_hours × fuel_consumption_per_hour`
   - Розраховується `motohours_accumulated = duration_hours`
   - Зменшується `fuel_stock.current_liters` на `fuel_consumed_liters`
   - Додається запис в `motohours_log`
   - Пишеться подія `SHIFT_STOPPED` в `event_log`

## Паливо (Fuel)

### Прихід палива на склад
1. **Робочий час** → HTTP 403
2. **Ліміт складу** — `current_liters + liters <= max_limit_liters` → HTTP 409 "Перевищення ліміту складу"
3. **Автоматично:** оновлюється `fuel_stock.current_liters`, пишеться `FUEL_DELIVERED` в `event_log`
4. **Атомарно** — в одній транзакції: запис доставки + оновлення stock + event

### Заправка генератора
1. **Робочий час** → HTTP 403
2. **Генератор НЕ працює** — заправка під час активної зміни ЗАБОРОНЕНА → HTTP 409 "Заправка під час роботи заборонена"
3. **Достатньо палива** — `fuel_stock.current_liters >= liters` → HTTP 409 "Недостатньо палива на складі"
4. **Місткість баку** — `tank_level_before + liters <= tank_capacity_liters` → HTTP 409 "Перевищення місткості баку"
5. **Автоматично:** зменшується `fuel_stock.current_liters`, пишеться `FUEL_REFILLED` в `event_log`
6. **Атомарно** — в одній транзакції

### Попередження по паливу
- `warning_active` = `current_liters <= warning_level_liters` (жовтий)
- `critical_active` = `current_liters <= warning_level_liters / 2` (червоний)

## ТО (Maintenance)

1. ТО фіксується вручну адміністратором
2. При фіксації вказуються поточні мотогодини та дата
3. `next_service_at_hours` = поточні мотогодини + `to_interval_hours`
4. `to_warning_active` = `hours_to_next_to <= to_warning_before_hours`

## Корекції (Adjustments)

Тільки ADMIN може створювати корекції.
Типи корекцій:
- `MOTOHOURS_ADJUST` — ручна корекція мотогодин
- `FUEL_STOCK_ADJUST` — корекція складу палива
- `FUEL_TANK_ADJUST` — корекція рівня в баку генератора
- `OIL_STOCK_ADJUST` — корекція запасів мастила
- `INITIAL_DATA` — введення початкових даних
- `TO_DATE_ADJUST` — корекція дати/мотогодин ТО

Кожна корекція:
- Зберігає `value_before`, `value_after`, `delta`
- Вимагає `reason` (обов'язкове)
- Автоматично оновлює відповідний запис в БД
- Пишеться `ADJUSTMENT_CREATED` в `event_log`

## Графік відключень

- `GET /api/outage/next` повертає найближче майбутнє відключення
- Логіка: `outage_date > today` АБО `(outage_date == today AND hour_start > current_hour)`, упорядковано
- Відображається на дашборді як "Наступне відключення"

## Системні налаштування

- `work_time_start` / `work_time_end` — дозволений час для операцій (Europe/Kyiv)
- Дефолт при першому старті: `07:00 – 22:00`
- Змінити може тільки ADMIN

## EventLog — типи подій

```
SHIFT_STARTED          # запуск генератора
SHIFT_STOPPED          # зупинка генератора
SYSTEM_SETTINGS_UPDATED
FUEL_DELIVERED         # прихід палива
FUEL_REFILLED          # заправка генератора
FUEL_STOCK_UPDATED
OIL_STOCK_UPDATED
ADJUSTMENT_CREATED
GENERATOR_CREATED
GENERATOR_UPDATED
GENERATOR_SETTINGS_UPDATED
GENERATOR_DEACTIVATED
MAINTENANCE_PERFORMED
```
