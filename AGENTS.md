# AGENTS.md — Контекст для AI-агентів

Цей файл призначений для будь-якого AI-агента (Copilot, Claude, GPT, Gemini тощо),
що підключається до репозиторію. Прочитай його першим.

## Що це за проєкт

**GenControl** — внутрішній веб-додаток для управління бензиновими генераторами.
Використовується командою з 3-5 осіб (адміністратор + оператори + глядачі).

### Основні функції
- Запуск та зупинка генератора (зміни)
- Облік витрат палива в реальному часі
- Управління складом палива (прихід, заправка)
- Облік мастила
- Мотогодини та нагадування про ТО
- Графік відключень електроенергії
- Журнал всіх подій
- Дашборд з живими даними

## Структура репозиторію

```
gen-control/
├── backend/                  # FastAPI бекенд
│   ├── app/
│   │   ├── common/           # enums, exceptions, utils
│   │   ├── config.py         # Pydantic Settings з .env
│   │   ├── db/               # session, redis
│   │   ├── main.py           # точка входу, lifespan, routers
│   │   └── modules/          # бізнес-модулі
│   │       ├── auth/
│   │       ├── users/
│   │       ├── generators/
│   │       ├── motohours/
│   │       ├── rules/        # RulesService
│   │       ├── shifts/
│   │       ├── fuel/
│   │       ├── oil/
│   │       ├── adjustments/
│   │       ├── outage/
│   │       ├── eventlog/
│   │       └── dashboard/
│   ├── alembic/
│   │   └── versions/         # V001–V005
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # Next.js PWA
│   ├── app/                  # App Router сторінки
│   ├── components/           # UI компоненти
│   ├── hooks/                # useAuth, useDashboard, useShiftTimer
│   ├── lib/                  # api.ts, utils.ts
│   ├── types/                # TypeScript типи
│   └── public/               # manifest.json, sw.js, icons
├── docs/
│   ├── conventions.md        # правила коду
│   ├── api-map.md            # всі ендпоінти
│   ├── business-rules.md     # бізнес-логіка
│   └── deployment.md         # деплой
├── AGENTS.md                 # цей файл
└── ARCHITECTURE.md           # детальна архітектура
```

## Перед тим як щось міняти

1. Прочитай `ARCHITECTURE.md` — щоб розуміти залежності між модулями
2. Прочитай `docs/business-rules.md` — щоб не порушити бізнес-логіку
3. Прочитай `docs/conventions.md` — щоб дотримуватись стилю коду
4. Перевір `docs/api-map.md` — щоб не дублювати ендпоінти

## Чого НЕ робити

- ❌ Не додавати дефолтні значення для `JWT_SECRET`, `DB_PASSWORD`, `ADMIN_PASSWORD` в `config.py`
- ❌ Не використовувати `float` для палива, мастила, мотогодин — тільки `Decimal`
- ❌ Не робити кілька окремих `db.commit()` в одній бізнес-операції — тільки транзакції
- ❌ Не пропускати виклик `RulesService` перед операціями зі змінами та паливом
- ❌ Не забувати писати в `event_log` після кожної операції
- ❌ Не використовувати `datetime.now()` без явного timezone — завжди `timezone.utc` або `ZoneInfo("Europe/Kyiv")`
- ❌ Не змінювати існуючі Alembic міграції — тільки нові
