# Getting Started

## Передумови

- Python 3.11+
- Docker + Docker Compose
- [uv](https://github.com/astral-sh/uv)

## 1. Середовище

```bash
cp .env.example .env
# Відредагуй .env — заповни реальні значення
```

## 2. Інфраструктура (PostgreSQL + Redis)

```bash
docker-compose up -d
```

## 3. Залежності

```bash
uv sync
```

## 4. Міграції

```bash
uv run alembic upgrade head
```

## 5. Запуск сервера

```bash
uv run uvicorn app.main:app --reload
```

API доступне на: http://localhost:8000

Docs: http://localhost:8000/docs

## Структура проєкту

Див. [ARCHITECTURE.md](./ARCHITECTURE.md) — повна архітектура.

Дів. [INVARIANTS.md](./INVARIANTS.md) — системні інваріанти (читати обов'язково перед реалізацією бізнес-логіки).

Дів. [EVENT_SCHEMA.md](./EVENT_SCHEMA.md) — схема event_log.
