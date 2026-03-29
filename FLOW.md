# FLOW.md — Покрокові флоу ключових операцій

> Цей файл описує **як** працюють основні операції в системі — що відбувається всередині, які перевірки запускаються,
> що записується в БД і що повертається клієнту.
> Всі флоу зняті з реального коду (`service.py`, `rules/service.py`).

---

## RulesService — центральний шлюз перевірок

`backend/app/modules/rules/service.py` — викликається до кожної змінюючої операції.

| Метод | Що перевіряє | Raises |
|---|---|---|
| `check_working_hours()` | `now_kyiv` між `work_time_start` і `work_time_end` | `403 ForbiddenException` |
| `check_no_active_shift(generator_id)` | чи є ACTIVE-зміна для цього генератора | `409 ConflictException` |
| `check_only_one_generator_active()` | чи є ACTIVE-зміна будь-якого генератора | `409 ConflictException` |
| `check_min_pause_between_starts(generator_id)` | чи минуло достатньо часу після останньої зміни | `409 ConflictException` |

---

## FLOW 1: Start Shift (`POST /api/shifts/start`)

**Хто:** ADMIN або OPERATOR · **Таймзона:** в робочий час

```
User → POST /api/shifts/start { generator_id }
  │
  ├─► RulesService.check_working_hours()
  │     now_kyiv в [work_time_start .. work_time_end]?
  │     └─ НІ → 403 "Дії заборонені поза робочим часом"
  │
  ├─► RulesService.check_only_one_generator_active()
  │     get_any_active() → є хоч одна ACTIVE-зміна в системі?
  │     └─ ТАК → 409 "Інший генератор вже працює"
  │
  ├─► RulesService.check_no_active_shift(generator_id)
  │     get_active_for_generator(generator_id) → є активна зміна?
  │     └─ ТАК → 409 "Вже є активна зміна #N"
  │
  ├─► RulesService.check_min_pause_between_starts(generator_id)
  │     остання CLOSED-зміна + min_pause_between_starts_min
  │     └─ ЗАНАДТО мало часу → 409 "Генератор на паузі, залишилось N хв."
  │
  ├─► GeneratorRepository.get_by_id(generator_id)
  │     └─ НЕ ІСНУЄ → 404 / is_active=False → 409
  │
  ├─► ShiftRepository.get_next_shift_number()
  │     MAX(shift_number) + 1 (або 1 якщо змін немає)
  │
  ├─► ShiftRepository.create(Shift)
  │     Shift { status=ACTIVE, started_by=user.id, started_at=now_utc }
  │
  └─► EventLog.add(SHIFT_STARTED)
        meta: { shift_number, generator_id, generator_name }

← Response 201: ShiftResponse
```

---

## FLOW 2: Stop Shift (`POST /api/shifts/{id}/stop`)

**Хто:** ADMIN або OPERATOR · зупинити чужу зміну може тільки ADMIN

```
User → POST /api/shifts/{id}/stop
  │
  ├─► RulesService.check_working_hours()
  │     └─ НІ → 403
  │
  ├─► ShiftRepository.get_by_id(id)
  │     └─ НЕ ІСНУЄ → 404
  │     └─ shift.status != ACTIVE → 409 "Зміна не активна"
  │
  ├─► Перевірка власника зміни
  │     shift.started_by == current_user.id OR role == ADMIN?
  │     └─ НІ → 403 "Тільки ADMIN може зупинити чужу зміну"
  │
  ├─► Розрахунок тривалості
  │     duration_minutes = (now_utc - shift.started_at).total_seconds() / 60
  │
  ├─► Розрахунок витрат палива
  │     gen_settings.fuel_consumption_per_hour існує?
  │     └─ ТАК: fuel_consumed = (duration_min / 60) * consumption_per_hour
  │     └─ НІ: fuel_consumed = None
  │
  ├─► Розрахунок мотогодин
  │     motohours_accumulated = duration_minutes / 60
  │
  ├─► ShiftRepository.update(shift)
  │     shift { status=CLOSED, stopped_by, stopped_at, duration_minutes,
  │              fuel_consumed_liters, motohours_accumulated }
  │
  ├─► MotohoursRepository: розрахунок total_after
  │     total_after = initial_motohours + сума_всіх_логів + motohours_accumulated
  │
  ├─► MotohoursLog.add
  │     { generator_id, shift_id, hours_added, total_after }
  │
  └─► EventLog.add(SHIFT_STOPPED)
        meta: { shift_number, duration_minutes, fuel_consumed_liters, motohours_accumulated }

← Response 200: ShiftResponse (status=CLOSED)
```

> ⚠️ Мотогодини не видаляються з `fuel_stock`. Тільки заправка (`create_refill`) зменшує склад.

---

## FLOW 3: Fuel Delivery (`POST /api/fuel/deliveries`)

**Хто:** ADMIN або OPERATOR

```
User → POST /api/fuel/deliveries { liters, check_number?, delivered_by_name? }
  │
  ├─► RulesService.check_working_hours()
  │     └─ НІ → 403
  │
  ├─► FuelRepository.get_stock()
  │     └─ НЕ ІСНУЄ → 404 (seeder гарантує що завжди є)
  │
  ├─► Перевірка ліміту складу
  │     current_liters + liters > max_limit_liters?
  │     └─ ТАК → 409 "Перевищення ліміту складу"
  │
  ├─► stock_before = current_liters
  │     stock_after  = current_liters + liters
  │
  ├─► FuelDelivery.create
  │     { fuel_type, liters, check_number, delivered_by_name,
  │       accepted_by=user.id, stock_before, stock_after }
  │
  ├─► fuel_stock.current_liters = stock_after  (одна транзакція)
  │
  └─► EventLog.add(FUEL_DELIVERED)
        meta: { liters, check_number, stock_before, stock_after }

← Response 201: FuelDeliveryResponse
```

---

## FLOW 4: Fuel Refill (`POST /api/fuel/refills`)

**Хто:** ADMIN або OPERATOR · заборонено під час активної зміни

```
User → POST /api/fuel/refills { generator_id, liters, tank_level_before }
  │
  ├─► RulesService.check_working_hours()
  │     └─ НІ → 403
  │
  ├─► ShiftRepository.get_active_for_generator(generator_id)
  │     └─ ACTIVE зміна існує → 409 "Заправка під час роботи заборонена"
  │
  ├─► FuelRepository.get_stock()
  │     current_liters < liters? → 409 "Недостатньо палива на складі"
  │
  ├─► Перевірка місткості бака
  │     tank_level_before + liters > tank_capacity_liters?
  │     └─ ТАК → 409 "Перевищення місткості бака"
  │
  ├─► tank_level_after = tank_level_before + liters
  │     stock_before    = current_liters
  │     stock_after     = current_liters - liters
  │
  ├─► FuelRefill.create
  │     { generator_id, performed_by=user.id, liters,
  │       tank_level_before, tank_level_after, stock_before, stock_after }
  │
  ├─► fuel_stock.current_liters = stock_after  (одна транзакція)
  │
  └─► EventLog.add(FUEL_REFILLED)
        meta: { liters, tank_before, tank_after, stock_before, stock_after }

← Response 201: FuelRefillResponse
```

> ⚠️ `tank_level_before` — значення вводить **користувач**. Система не розраховує рівень бака самостійно.

---

## FLOW 5: Auth Login (`POST /api/auth/login`)

```
User → POST /auth/login { username, password }
  │
  ├─► UserRepository.get_by_username(username)
  │     └─ НЕ ІСНУє → 401
  │
  ├─► bcrypt.verify(password, user.password_hash)
  │     └─ НІ → 401
  │
  ├─► user.is_active?
  │     └─ НІ → 401
  │
  ├─► JWT.encode({ sub: user.id, role: user.role, exp: now+ttl })
  │
  ├─► Redis.set(token, user.id, ex=ttl)  — stateful валідація
  │
  └─► EventLog.add(USER_LOGIN)

← Response 200: { access_token, token_type: "bearer" }
```

> ⚠️ JWT підписаний, але також зберігається в Redis. Логаут — видаляє ключ з Redis, тому старий токен перестає працювати навіть якщо не витік.

---

## FLOW 6: Dashboard Summary (`GET /api/dashboard/summary`)

```
User → GET /api/dashboard/summary
  │
  ├─► ShiftRepository.get_any_active()
  │     └─ є → active_shift { id, shift_number, generator_name, started_at, started_by_name }
  │     └─ немає → active_shift: null
  │
  ├─► FuelRepository.get_stock()
  │     → { current_liters, max_limit, warning_level }
  │     warning_active  = current_liters <= warning_level_liters
  │     critical_active = current_liters <= warning_level_liters * 0.5  (приклад)
  │
  ├─► MotohoursRepository.get_total_today()
  │     → motohours_today
  │
  ├─► OutageRepository.get_next()
  │     → next_outage { outage_date, hour_start, hour_end, note } | null
  │
  └─► Перевірка TO для кожного активного генератора
        total_motohours vs next_service_at_hours
        → to_warning: { active, hours_remaining }

← Response 200: DashboardSummaryResponse
```

> ⚠️ Dashboard читає дані, нічого не записує. Ніколи не додавай туди сайд ефектів.

---

## FLOW 7: Сеедер (запуск бекенду, `lifespan`)

```
uvicorn start → lifespan()
  │
  ├─► DB: створити ролі (ADMIN, OPERATOR, VIEWER) якщо немає
  │
  ├─► DB: створити адмін-користувача
  │     username=ADMIN_USERNAME, password=bcrypt(ADMIN_PASSWORD)
  │     └─ якщо username вже існує → пропустити
  │
  ├─► DB: створити system_settings (07:00–22:00)
  │     └─ якщо запис вже є → пропустити
  │
  └─► DB: створити fuel_stock (A95, 0л / макс 200л / попередж. 30л)
        └─ якщо запис вже є → пропустити

→ Бекенд готовий
```

---

## Загальні правила флоу

- Усі змінюючі операції (не GET) вимагають **робочий час** (`check_working_hours`)
- Усі зміни до `fuel_stock` робляться в одній транзакції разом з записом delivery/refill
- `motohours_accumulated` накопичується через `MotohoursLog`, не на живому полі генератора
- Центральний час — **UTC** (бекенд), перевірка робочого часу — переводиться в **Europe/Kyiv**
- Усі фінансові числа (літри, години) — `Decimal`, ніколи `float` для розрахунків
- Кожна змінююча операція пише подію в `event_log` (дивись `EventType` enum)
