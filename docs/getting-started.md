# Getting Started

## 1. Середовище
```bash
cp .env.example .env
# Відредагуй .env — заповни реальні значення
```

## 2. Інфраструктура
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
