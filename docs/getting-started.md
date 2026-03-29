# Getting Started

## Вимоги

- Python 3.11+
- Docker + Docker Compose
- [uv](https://docs.astral.sh/uv/) (менеджер залежностей)

## 1. Налаштування середовища

```bash
cp .env.example .env
# Відредагуй .env — заповни реальні значення для DB_URL, REDIS_URL тощо
```

## 2. Запуск інфраструктури

```bash
docker-compose up -d
# PostgreSQL буде доступний на localhost:5432
# Redis — на localhost:6379
```

## 3. Встановлення залежностей

```bash
uv sync
```

## 4. Міграції бази даних

```bash
uv run alembic upgrade head
```

## 5. Запуск сервера

```bash
uv run uvicorn app.main:app --reload
# API доступне на http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

## Структура проєкту

Див. [ARCHITECTURE.md](./ARCHITECTURE.md) для детального опису модулів.

## Системні інваріанти

Перед реалізацією будь-якої бізнес-логіки обов'язково прочитай [INVARIANTS.md](./INVARIANTS.md).

## Схема подій

Опис усіх типів event_log та структури meta: [EVENT_SCHEMA.md](./EVENT_SCHEMA.md).
