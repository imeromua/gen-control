# Getting Started

## Передумови

- Python 3.11+
- Docker + Docker Compose
- [uv](https://github.com/astral-sh/uv)

## 1. Клонування та середовище

```bash
git clone https://github.com/imeromua/gen-control.git
cd gen-control

# Скопіюй та відредагуй змінні оточення
cp .env.example .env
# Відкрий .env і заповни реальні значення
```

## 2. Запуск інфраструктури

```bash
docker-compose up -d
# PostgreSQL буде на localhost:5432
# Redis буде на localhost:6379
```

## 3. Встановлення залежностей

```bash
uv sync
```

## 4. Міграції БД

```bash
uv run alembic upgrade head
```

## 5. Запуск сервера

```bash
uv run uvicorn app.main:app --reload
```

Сервер буде доступний на: http://localhost:8000  
Документація API: http://localhost:8000/docs

## Перевірка

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

## Корисні команди

```bash
# Запуск тестів
uv run pytest

# Лінтер
uv run ruff check .

# Форматування
uv run ruff format .
```
