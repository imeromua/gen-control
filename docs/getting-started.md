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
# Піднімає PostgreSQL + Redis
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
# API доступне на http://localhost:8000
# Docs: http://localhost:8000/docs
```

## Перевірка

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

## Структура .env

Див. `.env.example` — всі змінні описані там з коментарями.
