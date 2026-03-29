# Conventions — Правила коду GenControl

## Структура модуля (бекенд)

Кожен модуль ОБОВ'ЯЗКОВО містить:
```
modules/<name>/
├── __init__.py
├── router.py      # FastAPI роутер, залежності, HTTP
├── service.py     # бізнес-логіка
├── repository.py  # SQL запити через SQLAlchemy
├── models.py      # SQLAlchemy ORM моделі
└── schemas.py     # Pydantic схеми (Request/Response)
```

## Іменування

### Python
```python
# Класи
class FuelService:          # PascalCase
class FuelRepository:
class FuelStock:            # ORM модель
class FuelStockResponse:    # Pydantic схема

# Змінні та функції
async def create_delivery(self, ...) -> FuelDelivery:
fuel_stock = await self.repo.get_stock()

# Константи
KYIV_TZ = ZoneInfo("Europe/Kyiv")
```

### TypeScript / Next.js
```typescript
// Компоненти — PascalCase
export function ActiveShiftCard() {}
export function FuelStockCard() {}

// Хуки — camelCase з use
export function useDashboard() {}
export function useShiftTimer() {}

// Типи — PascalCase
interface DashboardResponse {}
type ShiftStatus = 'ACTIVE' | 'CLOSED'
```

## Типи даних

```python
# ✅ ПРАВИЛЬНО — для палива, мастила, мотогодин
from decimal import Decimal
current_liters: Decimal = Decimal("87.5")

# ❌ НЕПРАВИЛЬНО
current_liters: float = 87.5

# ✅ UUID як PK
import uuid
id: uuid.UUID = uuid.uuid4()

# ✅ Timezone-aware datetime
from datetime import datetime, timezone
now = datetime.now(tz=timezone.utc)

# ✅ Kyiv час
from zoneinfo import ZoneInfo
KYIV_TZ = ZoneInfo("Europe/Kyiv")
now_kyiv = datetime.now(tz=timezone.utc).astimezone(KYIV_TZ)
```

## Транзакції (ОБОВ'ЯЗКОВО для операцій з паливом)

```python
# ✅ ПРАВИЛЬНО — атомарна операція
async def create_delivery(self, ...):
    async with self.db.begin():
        delivery = FuelDelivery(...)
        self.db.add(delivery)
        stock.current_liters = stock_after
        await self.db.flush()
        event = EventLog(...)
        self.db.add(event)
    # commit відбувається автоматично при виході з блоку
    return delivery

# ❌ НЕПРАВИЛЬНО — кілька окремих commit
async def create_delivery(self, ...):
    await self.repo.create(delivery)   # commit #1
    await self.repo.update_stock(...)  # commit #2 — небезпечно!
```

## Помилки

```python
from app.common.exceptions import (
    ConflictException,    # 409
    ForbiddenException,   # 403
    NotFoundException,    # 404
)

# Використання:
raise ConflictException(detail="Вже є активна зміна #42")
raise ForbiddenException(detail="Дії заборонені поза робочим часом")
raise NotFoundException(detail="Генератор не знайдений")
```

## EventLog — обов'язково після кожної операції

```python
# Після будь-якої бізнес-операції:
event = EventLog(
    generator_id=generator_id,       # або None якщо не стосується
    event_type=EventType.FUEL_DELIVERED,
    created_by=current_user.id,
    meta={
        "liters": float(liters),
        "stock_before": float(stock_before),
        "stock_after": float(stock_after),
    }
)
self.db.add(event)
```

## Alembic міграції

```python
# Файл: backend/alembic/versions/V006__назва.py
"""
V006 короткий опис

Revision ID: v006
Revises: v005          # ЗАВЖДИ вказувати попередню
Create Date: ...
"""

revision = "v006"
down_revision = "v005"   # ← ОБОВ'ЯЗКОВО

def upgrade() -> None:
    op.create_table(...)

def downgrade() -> None:
    op.drop_table(...)   # ← ЗАВЖДИ реалізовувати
```

## API роутери

```python
# Префікс визначається в main.py (prefix="/api")
# В роутері — тільки відносний шлях
router = APIRouter(prefix="/fuel", tags=["fuel"])

@router.get("/stock", response_model=FuelStockResponse)
async def get_fuel_stock(
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    ...
```

## Залежності авторизації

```python
from app.modules.auth.dependencies import (
    require_admin,               # тільки ADMIN
    require_admin_or_operator,   # ADMIN або OPERATOR
    get_current_user,            # будь-який авторизований
)
```
