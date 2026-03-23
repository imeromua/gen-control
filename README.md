# GenControl

Веб-сервіс обліку та контролю роботи бензинових генераторів на об'єкті.

**Стек:** Python 3.12 · FastAPI · PostgreSQL · Redis · Docker

---

## Структура проєкту

```
gencontrol/
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

API буде доступне за адресою: <http://localhost:8080>

Документація Swagger: <http://localhost:8080/docs>

---

## Застосування міграцій вручну (поза Docker)

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
```

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
