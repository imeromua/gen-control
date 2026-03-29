# ARCHITECTURE.md — Архітектура GenControl

## Загальна схема

```
┌─────────────────────────────────────────┐
│           Next.js PWA (Frontend)         │
│  Dashboard │ Shifts │ Fuel │ Generators  │
│            SWR polling (30s)             │
└──────────────────┬──────────────────────┘
                   │ HTTP REST JSON
┌──────────────────▼──────────────────────┐
│           FastAPI Backend               │
│  JWT Auth (Redis) │ CORS │ Middleware   │
├─────────────────────────────────────────┤
│  Modules: auth, users, generators,      │
│  motohours, rules, shifts, fuel, oil,   │
│  adjustments, outage, eventlog,         │
│  dashboard                              │
└────────────┬────────────────┬───────────┘
             │                │
    ┌────────▼───────┐  ┌─────▼──────┐
    │  PostgreSQL     │  │   Redis    │
    │  (основні дані) │  │  (JWT)     │
    └────────────────┘  └────────────┘
```

## Ланцюжок залежностей модулів

```
auth
  └── users (get_by_username, get_by_id)

users
  └── (незалежний)

generators
  └── users (FK: created_by)

motohours
  └── generators (FK: generator_id)
  └── users (FK: performed_by)

rules (RulesService)
  └── shifts (ShiftRepository)
  └── generators (GeneratorRepository)
  └── shifts (SystemSettingsRepository)

shifts
  └── generators
  └── users
  └── rules ← перевірки перед стартом
  └── motohours ← запис при зупинці

fuel
  └── generators (fuel_type з settings)
  └── users (FK: accepted_by, performed_by)
  └── rules ← перевірки перед заправкою
  └── eventlog ← запис кожної операції

oil
  └── generators
  └── users

adjustments
  └── users
  └── fuel (оновлення stock)
  └── oil (оновлення stock)
  └── motohours (корекція)
  └── eventlog

outage
  └── users

eventlog
  └── generators (читання)
  └── (тільки читання, без запису через API)

dashboard
  └── ВСІ модулі (агрегація)
```

## База даних — таблиці

### V001 — users, roles
| Таблиця | Ключові поля |
|---|---|
| `roles` | id, name (ADMIN/OPERATOR/VIEWER) |
| `users` | id, full_name, username, password_hash, role_id |

### V002 — generators, motohours
| Таблиця | Ключові поля |
|---|---|
| `generators` | id, name, type, is_active |
| `generator_settings` | id, generator_id, fuel_type, tank_capacity_liters, fuel_consumption_per_hour, to_interval_hours, to_warning_before_hours |
| `motohours_log` | id, generator_id, hours_added, source (SHIFT/MANUAL), ref_id |
| `maintenance_log` | id, generator_id, performed_by, motohours_at_service, next_service_at_hours |
| `event_log` | id, generator_id, event_type, meta(JSON), created_by, created_at |

### V003 — shifts, system_settings
| Таблиця | Ключові поля |
|---|---|
| `system_settings` | id, work_time_start, work_time_end, updated_by |
| `shifts` | id, shift_number, generator_id, started_by, started_at, stopped_by, stopped_at, duration_minutes, fuel_consumed_liters, motohours_accumulated, status (ACTIVE/CLOSED) |

### V004 — fuel, oil
| Таблиця | Ключові поля |
|---|---|
| `fuel_stock` | id, fuel_type, current_liters, max_limit_liters, warning_level_liters |
| `fuel_deliveries` | id, fuel_type, liters, check_number, delivered_by_name, accepted_by, stock_before, stock_after |
| `fuel_refills` | id, generator_id, performed_by, liters, tank_level_before, tank_level_after, stock_before, stock_after |
| `oil_stock` | id, generator_id, oil_type, current_quantity, unit (LITERS/KG) |

### V005 — adjustments, outage
| Таблиця | Ключові поля |
|---|---|
| `adjustments` | id, adjustment_type, entity_type, entity_id, value_before, value_after, delta, reason, performed_by |
| `outage_schedule` | id, outage_date, hour_start, hour_end, note, created_by |

## Авторизація

### Ролі та доступ
| Ендпоінт | ADMIN | OPERATOR | VIEWER |
|---|---|---|---|
| Управління користувачами | ✅ | ❌ | ❌ |
| Налаштування генераторів | ✅ | ❌ | ❌ |
| Перегляд генераторів/статусу | ✅ | ✅ | ❌ |
| Старт/стоп зміни | ✅ | ✅ | ❌ |
| Прихід палива / заправка | ✅ | ✅ | ❌ |
| Перегляд складу палива | ✅ | ✅ | ❌ |
| Журнал подій / дашборд | ✅ | ✅ | ❌ |
| Графік відключень (читання) | ✅ | ✅ | ❌ |
| Корекції (adjustments) | ✅ | ❌ | ❌ |

### JWT Flow
```
POST /auth/login → JWT token → зберігається в Redis
Authorization: Bearer <token> → перевірка в Redis
POST /auth/logout → видалення з Redis
```

## RulesService — перевірки

```python
class RulesService:
    check_working_hours()              # час в межах system_settings
    check_no_active_shift(gen_id)      # немає активної зміни
    check_only_one_generator_active()  # тільки один генератор
    check_min_pause_between_starts()   # мінімум 30 хв між запусками
```

Викликається в `shifts/service.py` та `fuel/service.py`.

## Frontend архітектура

### Сторінки
| Маршрут | Компонент | Доступ |
|---|---|---|
| `/` | Dashboard | ADMIN + OPERATOR |
| `/shifts` | Журнал змін | ADMIN + OPERATOR |
| `/fuel` | Паливо | ADMIN + OPERATOR |
| `/generators` | Генератори | ADMIN |
| `/outage` | Графік відключень | ADMIN + OPERATOR |
| `/events` | Журнал подій | ADMIN + OPERATOR |
| `/login` | Авторизація | Всі |

### Живі дані на дашборді
- **Polling** (SWR, 30с) → `GET /api/dashboard/summary`
- **Таймер** (tick/сек, клієнт) → рахує від `shift.started_at`
  - Час роботи
  - Оцінка витрати палива: `duration_hours × fuel_consumption_per_hour`
  - Поточні мотогодини: `motohours_total + duration_hours`
