# GenControl

Веб-сервіс обліку та контролю роботи бензинових генераторів на об'єкті.

**Бекенд:** Python 3.12 · FastAPI · PostgreSQL · Redis · Docker

**Фронтенд:** Next.js 14 · TypeScript · Tailwind CSS · shadcn/ui · PWA

---

## Структура проєкту

```
gen-control/
├── backend/
│   ├── app/
│   │   ├── main.py              # Точка входу, seeder
│   │   ├── config.py            # Pydantic Settings
│   │   ├── db/                  # Engine, session, Redis
│   │   ├── common/              # Enums, exceptions, utils
│   │   └── modules/
│   │       ├── auth/            # Login / logout / me
│   │       └── users/           # CRUD користувачів (тільки ADMIN)
│   ├── alembic/                 # Міграції БД
│   ├── .env.example
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   ├── icons/               # PWA іконки 192x192, 512x512
│   │   ├── manifest.json        # PWA manifest
│   │   └── sw.js                # Service worker (next-pwa)
│   ├── app/
│   │   ├── layout.tsx           # Root layout, ThemeProvider
│   │   ├── page.tsx             # / → Dashboard
│   │   ├── login/               # /login — сторінка авторизації
│   │   ├── shifts/              # /shifts — журнал змін
│   │   ├── fuel/                # /fuel — паливо та графіки
│   │   ├── generators/          # /generators — налаштування (ADMIN)
│   │   ├── outage/              # /outage — графік відключень
│   │   └── events/              # /events — журнал подій
│   ├── components/              # UI-компоненти (shadcn/ui + layout)
│   ├── hooks/                   # useAuth, useDashboard, useShiftTimer
│   ├── lib/                     # api.ts, utils.ts
│   ├── types/                   # TypeScript типи API
│   ├── next.config.js           # next-pwa налаштування
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Швидкий старт

### 1. Клонуйте репозиторій та перейдіть у теку

```bash
git clone https://github.com/imeromua/gen-control.git
cd gen-control
```

### 2. Створіть `.env` з прикладу

```bash
cp backend/.env.example backend/.env
# Відредагуйте backend/.env — встановіть безпечні паролі та JWT_SECRET
```

### 3. Запустіть через Docker Compose

```bash
docker-compose up --build
```

| Сервіс | URL |
|--------|-----|
| Фронтенд (PWA) | <http://localhost:3000> |
| REST API | <http://localhost:8080> |
| Swagger UI | <http://localhost:8080/docs> |

---

## Застосування міграцій вручну (поза Docker)

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
```

---

## Сторінки фронтенду

| Сторінка | URL | Ролі |
|----------|-----|------|
| Дашборд | `/` | ADMIN, OPERATOR |
| Журнал змін | `/shifts` | ADMIN, OPERATOR |
| Паливо | `/fuel` | ADMIN, OPERATOR |
| Генератори | `/generators` | тільки ADMIN |
| Графік відключень | `/outage` | ADMIN, OPERATOR |
| Журнал подій | `/events` | ADMIN, OPERATOR |
| Авторизація | `/login` | — |

**Дашборд** оновлюється автоматично кожні 30 секунд (SWR polling). Під час активної зміни таймер тікає кожну секунду.

**PWA:** додаток можна встановити на мобільний пристрій або робочий стіл. Підтримуються темна/світла/системна теми.

---

## API ендпоінти

### Auth

| Метод | URL | Опис |
|-------|-----|------|
| POST | `/api/auth/login` | Логін, повертає JWT токен |
| POST | `/api/auth/logout` | Логаут, інвалідація токена |
| GET | `/api/auth/me` | Інфо про поточного користувача |

### Users (тільки ADMIN)

| Метод | URL | Опис |
|-------|-----|------|
| GET | `/api/users/` | Список користувачів |
| POST | `/api/users/` | Створити користувача |
| GET | `/api/users/{id}` | Отримати користувача |
| PATCH | `/api/users/{id}` | Оновити (ім'я, роль, активність) |
| DELETE | `/api/users/{id}` | Деактивувати користувача |

---

## Перший запуск

При першому старті автоматично:
- Створюються ролі: `ADMIN`, `OPERATOR`, `VIEWER`
- Створюється адмін-користувач з даних `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_FULLNAME` з `.env`

---

## Змінні оточення

Дивіться `backend/.env.example` для повного переліку.

Додаткові змінні для `docker-compose.yml`:

| Змінна | За замовчуванням | Опис |
|--------|-----------------|------|
| `FRONTEND_PORT` | `3000` | Порт фронтенду |
| `NEXT_PUBLIC_API_URL` | `http://backend:8080` | URL бекенд API для фронтенду |
| `SERVER_PORT` | `8080` | Порт бекенду |
