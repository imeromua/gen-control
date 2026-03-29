# Getting Started

## Вимоги

- Python 3.11+
- Docker + Docker Compose
- [uv](https://github.com/astral-sh/uv)

## 1. Середовище

```bash
cp .env.example .env
# Відредагуй .env — заповни реальні значення
```

## 2. Інфраструктура

```bash
docker-compose up -d
```

Перевірка:
```bash
docker-compose ps  # postgres та redis мають бути healthy
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

API доступне за адресою: http://localhost:8000

Документація: http://localhost:8000/docs

## Часті проблеми

| Проблема | Рішення |
|----------|---------|
| `connection refused` на DB | Перевір що postgres запущений: `docker-compose up -d postgres` |
| `alembic: command not found` | Використовуй `uv run alembic` |
| Порт 8000 зайнятий | `--port 8001` або зупини інший процес |
