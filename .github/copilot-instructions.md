# GenControl — Copilot Instructions

Цей файл читається автоматично при кожному запиті. Завжди враховуй цей контекст.

## Проєкт

GenControl — внутрішній веб-додаток для моніторингу та управління бензиновими генераторами.
Використовується операторами та адміністраторами для керування змінами, обліку палива, мастила, ТО та графіку відключень світла.

## Стек

### Backend (`/backend`)
- **FastAPI** (async) + **Python 3.11+**
- **PostgreSQL 15+** через **SQLAlchemy 2.0 async** + **asyncpg**
- **Redis** — зберігання JWT токенів (stateful auth)
- **Alembic** — міграції БД (`/backend/alembic/versions/`)
- **Pydantic v2** — схеми та конфіг
- **passlib[bcrypt]** — хешування паролів
- **python-jose** — JWT

### Frontend (`/frontend`)
- **Next.js 14** (App Router) + **TypeScript**
- **Tailwind CSS** + **shadcn/ui**
- **Lucide React** — іконки
- **SWR** — fetching + polling
- **next-themes** — темна/світла/системна тема
- **next-pwa** — PWA, service worker
- **Recharts** — графіки

## Архітектура бекенду

Кожен модуль: `router.py → service.py → repository.py → models.py → schemas.py`

Модулі:
- `auth` — логін, логаут, refresh
- `users` — CRUD користувачів, ролі
- `generators` — генератори та їх налаштування
- `motohours` — мотогодини, обслуговування
- `rules` — RulesService: перевірки перед операціями
- `shifts` — зміни (старт/стоп генератора)
- `fuel` — склад палива, доставки, заправки
- `oil` — облік мастила
- `adjustments` — ручні корекції даних
- `outage` — графік відключень електроенергії
- `eventlog` — журнал всіх подій (read-only)
- `dashboard` — агрегація даних для головного екрану

## Критичні правила

1. **Завжди async/await** — жодних sync операцій з БД
2. **Decimal** для палива, мастила, мотогодин — ніколи float
3. **Транзакції** — операції з паливом обов'язково в `async with db.begin()`
4. **RulesService** — викликати перед будь-якою бізнес-операцією
5. **Europe/Kyiv** — часовий пояс для всіх розрахунків дат
6. **event_log** — писати після КОЖНОЇ бізнес-операції
7. **UUID** як primary key скрізь
8. **Ролі**: ADMIN > OPERATOR > VIEWER

## Помилки

```python
from app.common.exceptions import (
    ConflictException,    # 409 — конфлікт стану
    ForbiddenException,   # 403 — заборонено правилами
    NotFoundException,    # 404 — не знайдено
)
```

## Міграції

Нова міграція завжди наступна по ланцюгу:
`V001 → V002 → V003 → V004 → V005 → ...`

Файл: `backend/alembic/versions/V00N__назва.py`

## Frontend правила

- Polling dashboard: `useDashboard` hook, кожні **30 секунд** (SWR)
- Таймер зміни: `useShiftTimer` hook, tick **кожну секунду** (клієнтський розрахунок)
- JWT зберігається в **httpOnly cookie**
- Редирект на `/login` якщо не авторизований
- OPERATOR не бачить сторінку `/generators`
