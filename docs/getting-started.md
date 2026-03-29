# Getting Started

## Вимоги

- Python 3.11+
- Docker & Docker Compose
- [uv](https://github.com/astral-sh/uv)

## 1. Клонування

```bash
git clone https://github.com/imeromua/gen-control.git
cd gen-control
```

## 2. Змінні середовища

```bash
cp .env.example .env
# Відкрий .env і заповни реальні значення
```

## 3. Інфраструктура (PostgreSQL + Redis)

```bash
docker-compose up -d
```

## 4. Залежності Python

```bash
uv sync
```

## 5. Міграції БД

```bash
uv run alembic upgrade head
```

## 6. Запуск сервера

```bash
uv run uvicorn app.main:app --reload
```

API доступне на: http://localhost:8000

Документація: http://localhost:8000/docs

## Корисні команди

```bash
# Запустити тести
uv run pytest

# Перевірити типи
uv run mypy app/

# Лінтер
uv run ruff check app/
```
