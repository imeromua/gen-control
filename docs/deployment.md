# Deployment Guide — Розгортання GenControl

## Варіант 1: Локально без Docker (розробка)

### Вимоги
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Linux Mint / Ubuntu

```bash
# PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE gencontrol;"
sudo -u postgres psql -c "CREATE USER gencontrol_user WITH PASSWORD 'yourpassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE gencontrol TO gencontrol_user;"

# Redis
sudo apt install -y redis-server
sudo systemctl start redis
redis-cli ping  # → PONG

# Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### Бекенд

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Відредагувати .env — вписати реальні значення!
nano .env

# Запустити міграції
alembic upgrade head

# Запустити сервер
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

✅ Swagger: http://localhost:8080/docs

### Фронтенд

```bash
cd frontend
npm install
echo 'NEXT_PUBLIC_API_URL=http://localhost:8080' > .env.local
npm run dev
```

✅ Додаток: http://localhost:3000

---

## Варіант 2: Docker Compose

```bash
# Скопіювати та налаштувати .env
cp backend/.env.example backend/.env
nano backend/.env

# Запустити все
docker-compose up -d

# Перевірити логи
docker-compose logs -f backend
```

✅ Бекенд: http://localhost:8080
✅ Фронтенд: http://localhost:3000

---

## .env — обов'язкові змінні

```env
# База даних
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gencontrol
DB_USERNAME=gencontrol_user
DB_PASSWORD=              # ← ОБОВ'ЯЗКОВО задати

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT — мінімум 32 символи, випадковий рядок
JWT_SECRET=              # ← ОБОВ'ЯЗКОВО задати

# Перший адмін
ADMIN_USERNAME=admin
ADMIN_PASSWORD=          # ← ОБОВ'ЯЗКОВО задати
ADMIN_FULLNAME=Адміністратор

# CORS — URL фронтенду
ALLOWED_ORIGINS=["http://localhost:3000"]

# Робочий час (за замовчуванням)
DEFAULT_WORK_TIME_START=07:00
DEFAULT_WORK_TIME_END=22:00
```

### Генерація JWT_SECRET
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Перший запуск — що відбувається автоматично

При старті бекенду (`lifespan`) автоматично:
1. Створюються ролі: ADMIN, OPERATOR, VIEWER
2. Створюється перший адмін з `.env` (якщо немає жодного)
3. Створюється `system_settings` (07:00–22:00)
4. Створюється `fuel_stock` (A95, 0/200 л)

---

## PWA — встановлення на Android

1. Відкрити `http://<ip-сервера>:3000` в Chrome
2. Меню (⋮) → "Додати на головний екран"
3. Додаток встановлено — відкривається як нативний

---

## Troubleshooting

### `alembic upgrade head` — помилка підключення
```bash
# Перевір що PostgreSQL запущений
sudo systemctl status postgresql
# Перевір .env — DB_HOST, DB_PORT, DB_NAME, DB_USERNAME, DB_PASSWORD
```

### CORS помилка в браузері
```
# В .env перевір:
ALLOWED_ORIGINS=["http://localhost:3000"]
# Перезапусти бекенд після зміни .env
```

### Redis не підключається
```bash
redis-cli ping  # має відповісти PONG
sudo systemctl start redis
```
