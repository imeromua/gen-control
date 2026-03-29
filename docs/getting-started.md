# Getting Started

## Вимоги

- Python 3.11+
- Docker + Docker Compose
- [uv](https://github.com/astral-sh/uv)

## 1. Середовище

```bash
cp .env.example .env
# Відредагуй .env — заповни реальні значення для DB_URL, REDIS_URL, SECRET_KEY
```

## 2. Інфраструктура

```bash
docker-compose up -d
# Підіймає PostgreSQL та Redis
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

Сервер доступний на: http://localhost:8000

Документація API: http://localhost:8000/docs

## Типові проблеми

| Проблема | Рішення |
|----------|---------|
| `connection refused` на PostgreSQL | Переконайся що `docker-compose up -d` виконано |
| `ModuleNotFoundError` | Виконай `uv sync` |
| Міграції не застосовані | Виконай `uv run alembic upgrade head` |
