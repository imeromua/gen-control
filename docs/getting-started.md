# Getting Started

## Вимоги

- Python 3.11+
- Docker + Docker Compose
- [uv](https://github.com/astral-sh/uv)

## 1. Середовище

```bash
cp .env.example .env
# Відредагуй .env — заповни реальні значення (DB_URL, REDIS_URL, SECRET_KEY)
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

Сервер запуститься на http://localhost:8000

Документація API: http://localhost:8000/docs

## Швидка перевірка

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```
