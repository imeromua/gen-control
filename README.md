# GenControl

Внутрішній веб-додаток для моніторингу та управління бензиновими генераторами на об'єкті.
Облік палива, мастила, мотогодин, змін, відключень електроенергії та журнал подій.

**Бекенд:** Python 3.11+ · FastAPI · PostgreSQL 15+ · Redis · Alembic · SQLAlchemy async

**Фронтенд:** Next.js 14 · TypeScript · Tailwind CSS · shadcn/ui · PWA · SWR

---

## 📚 Документація для AI-агентів

> Якщо ти AI-агент — прочитай ці файли **перед** будь-якими змінами.

| Файл | Зміст |
|---|---|
| [AGENTS.md](./AGENTS.md) | Загальний контекст, структура репо, що НЕ робити |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Схема системи, залежності модулів, таблиці БД, ролі |
| [FLOW.md](./FLOW.md) | Покрокові флоу ключових операцій з перевірками та сайд-ефектами |
| [docs/business-rules.md](./docs/business-rules.md) | Бізнес-правила: заборони, перевірки, автоматичні дії |
| [docs/conventions.md](./docs/conventions.md) | Правила коду: Decimal, UUID, транзакції, стиль |
| [docs/api-map.md](./docs/api-map.md) | Всі ендпоінти з методами та рівнями доступу |
| [docs/db-schema.md](./docs/db-schema.md) | SQL-схема всіх 14 таблиць |
| [docs/payload-examples.md](./docs/payload-examples.md) | JSON приклади запитів та відповідей |
| [docs/frontend-error-handling.md](./docs/frontend-error-handling.md) | Глобальна обробка помилок API, перехоплення 401, Offline-режим |
| [docs/deployment.md](./docs/deployment.md) | Запуск локально (Linux) та через Docker |
| [.github/copilot-instructions.md](./.github/copilot-instructions.md) | Автоматично читається GitHub Copilot |

---

## Функціональність

| Модуль | Що робить |
|---|---|
| **Auth** | Логін/логаут, JWT у Redis (stateful), ролі |
| **Users** | CRUD користувачів, ролі ADMIN / OPERATOR / VIEWER |
| **Generators** | Налаштування генераторів, статус, параметри споживання |
| **Motohours** | Облік мотогодин, журнал ТО, попередження про наближення ТО |
| **Shifts** | Запуск/зупинка генератора, автоматичний розрахунок витрат |
| **Fuel** | Склад палива, прийом, заправки генератора, попередження рівня |
| **Oil** | Облік запасів мастила по генераторах |
| **Adjustments** | Ручні коригування даних (тільки ADMIN) |
| **Outage** | Графік відключень електроенергії |
| **Event Log** | Журнал усіх подій (read-only) |
| **Dashboard** | Агрегований стан: активна зміна, паливо, ТО, наступне відключення |

---

## Структура проєкту

```
gen-control/
├── .github/
│   └── copilot-instructions.md   ← AI контекст (Copilot)
├── backend/
│   ├── app/
│   │   ├── main.py               # Точка входу, lifespan, seeder
│   │   ├── config.py             # Pydantic Settings з .env
│   │   ├── db/                   # Engine, session, Redis
│   │   ├── common/               # Enums, exceptions, utils
│   │   └── modules/
│   │       ├── auth/
│   │       ├── users/
│   │       ├── generators/
│   │       ├── motohours/
│   │       ├── rules/            # RulesService — перевірки перед операціями
│   │       ├── shifts/
│   │       ├── fuel/
│   │       ├── oil/
│   │       ├── adjustments/
│   │       ├── outage/
│   │       ├── eventlog/
│   │       └── dashboard/
│   ├── alembic/
│   │   └── versions/             # V001–V005
│   ├── .env.example
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── layout.tsx            # Root layout, ThemeProvider
│   │   ├── page.tsx              # / → Dashboard
│   │   ├── login/
│   │   ├── shifts/
│   │   ├── fuel/
│   │   ├── generators/
│   │   ├── outage/
│   │   └── events/
│   ├── components/               # shadcn/ui + layout компоненти
│   ├── hooks/                    # useAuth, useDashboard, useShiftTimer, useToast
│   ├── lib/                      # api.ts, utils.ts
│   ├── types/                    # TypeScript типи
│   ├── public/                   # manifest.json, sw.js, icons
│   ├── next.config.js            # next-pwa конфігурація
│   └── Dockerfile
├── docs/                         ← вся документація
├── AGENTS.md
├── ARCHITECTURE.md
├── FLOW.md                       ← покрокові флоу операцій
├── docker-compose.yml
└── README.md
```

---

## Швидкий старт

### Варіант 1 — Docker Compose

```bash
git clone https://github.com/imeromua/gen-control.git
cd gen-control

cp backend/.env.example backend/.env
# Відредагувати .env — вписати реальні паролі та JWT_SECRET
nano backend/.env

docker-compose up --build
```

| Сервіс | URL |
|---|---|
| Фронтенд (PWA) | http://localhost:3000 |
| REST API | http://localhost:8080 |
| Swagger UI | http://localhost:8080/docs |

### Варіант 2 — Локально без Docker (Linux Mint / Ubuntu)

Детальний гайд: [docs/deployment.md](./docs/deployment.md)

```bash
# Бекенд
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Фронтенд (новий термінал)
cd frontend
npm install
echo 'NEXT_PUBLIC_API_URL=http://localhost:8080' > .env.local
npm run dev
```

---

## Змінні оточення

Детанльно: [`backend/.env.example`](./backend/.env.example)

| Змінна | Опис |
|---|---|
| `DB_*` | Підключення до PostgreSQL |
| `REDIS_*` | Підключення до Redis |
| `JWT_SECRET` | Секрет для підпису токенів (обов'язково!) |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Перший адмін (створюється при старті) |
| `ALLOWED_ORIGINS` | CORS — URL фронтенду |
| `DEFAULT_WORK_TIME_START/END` | Початковий робочий час (07:00–22:00) |

> **Генерація JWT_SECRET:**
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```

---

## Перший запуск — що відбувається автоматично

При старті бекенду (`lifespan`):
1. Створюються ролі: `ADMIN`, `OPERATOR`, `VIEWER`
2. Створюється перший адмін з `.env` (якщо немає)
3. Ініціалізуються `system_settings` (07:00–22:00)
4. Ініціалізується `fuel_stock` (A95, 0 / 200 л)

---

## Сторінки фронтенду

| Сторінка | URL | Доступ |
|---|---|---|
| Дашборд | `/` | ADMIN, OPERATOR |
| Журнал змін | `/shifts` | ADMIN, OPERATOR |
| Паливо | `/fuel` | ADMIN, OPERATOR |
| Генератори | `/generators` | тільки ADMIN |
| Графік відключень | `/outage` | ADMIN, OPERATOR |
| Журнал подій | `/events` | ADMIN, OPERATOR |
| Авторизація | `/login` | Всі |

Дашборд оновлюється автоматично кожні **30 секунд** (SWR polling).
Таймер активної зміни тікає **кожну секунду** (клієнтський розрахунок).

**PWA:** встановлюється на Android/iOS як нативний додаток через Chrome → "Додати на головний екран".

---

## Ролі

| Дія | ADMIN | OPERATOR | VIEWER |
|---|---|---|---|
| Управління користувачами | ✅ | ❌ | ❌ |
| Налаштування генераторів | ✅ | ❌ | ❌ |
| Перегляд генераторів/статусу | ✅ | ✅ | ❌ |
| Старт/стоп зміни | ✅ | ✅ | ❌ |
| Прийом палива / заправка | ✅ | ✅ | ❌ |
| Перегляд складу палива | ✅ | ✅ | ❌ |
| Коригування даних | ✅ | ❌ | ❌ |
| Дашборд та журнали | ✅ | ✅ | ❌ |

---

## Міграції БД

```bash
# Застосувати всі міграції
alembic upgrade head

# Перевірити стан
alembic current

# Відкотити останню
alembic downgrade -1
```

Файли міграцій: `backend/alembic/versions/` (V001–V005)
