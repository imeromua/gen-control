# Getting Started

## 1. Середовище

```bash
cp .env.example .env
# Відредагуй .env — заповни реальні значення
```

## 2. Інфраструктура (PostgreSQL + Redis)

```bash
docker-compose up -d
```

## 3. Міграції

```bash
uv run alembic upgrade head
```

## 4. Запуск сервера

```bash
uv run uvicorn app.main:app --reload
```

Сервер доступний на http://localhost:8000

Документація API: http://localhost:8000/docs

## Вимоги

- Python 3.11+
- Docker + Docker Compose
- [uv](https://github.com/astral-sh/uv)

## Типові помилки

| Помилка | Причина | Рішення |
|---------|---------|----------|
| `connection refused` на PostgreSQL | docker не запущений | `docker-compose up -d` |
| `alembic.util.exc.CommandError` | міграції не застосовані | `uv run alembic upgrade head` |
| `ModuleNotFoundError` | залежності не встановлені | `uv sync` |
