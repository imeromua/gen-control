# Database Schema — Схема БД GenControl

БД: PostgreSQL 15+. Всі `id` — UUID. Час: `timestamp with time zone` (UTC).

---

## V001 — Користувачі

### `roles`
```sql
CREATE TABLE roles (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       VARCHAR(20) NOT NULL UNIQUE  -- ADMIN | OPERATOR | VIEWER
);
```

### `users`
```sql
CREATE TABLE users (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name      VARCHAR(100) NOT NULL,
    username       VARCHAR(50)  NOT NULL UNIQUE,
    password_hash  TEXT         NOT NULL,
    role_id        UUID         NOT NULL REFERENCES roles(id),
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

---

## V002 — Генератори

### `generators`
```sql
CREATE TABLE generators (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    model       VARCHAR(100),
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_by  UUID         REFERENCES users(id),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

### `generator_settings`
```sql
CREATE TABLE generator_settings (
    id                           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generator_id                 UUID        NOT NULL REFERENCES generators(id) ON DELETE CASCADE,
    fuel_type                    VARCHAR(20) NOT NULL DEFAULT 'A95',
    tank_capacity_liters         DECIMAL(10,2) NOT NULL DEFAULT 100,
    fuel_consumption_per_hour    DECIMAL(10,3) NOT NULL DEFAULT 10,
    to_interval_hours            DECIMAL(10,1) NOT NULL DEFAULT 250,
    to_warning_before_hours      DECIMAL(10,1) NOT NULL DEFAULT 10,
    updated_at                   TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
```

### `motohours_log`
```sql
CREATE TABLE motohours_log (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generator_id  UUID         NOT NULL REFERENCES generators(id),
    hours_added   DECIMAL(10,2) NOT NULL,
    source        VARCHAR(20)  NOT NULL,  -- SHIFT | MANUAL
    ref_id        UUID,                   -- shift_id або adjustment_id
    performed_by  UUID         REFERENCES users(id),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

### `maintenance_log`
```sql
CREATE TABLE maintenance_log (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generator_id         UUID          NOT NULL REFERENCES generators(id),
    performed_by         UUID          REFERENCES users(id),
    motohours_at_service DECIMAL(10,2) NOT NULL,
    next_service_at_hours DECIMAL(10,2) NOT NULL,
    notes                TEXT,
    performed_at         TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
```

### `event_log`
```sql
CREATE TABLE event_log (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generator_id  UUID         REFERENCES generators(id),
    event_type    VARCHAR(50)  NOT NULL,  -- EventType enum
    meta          JSONB,                  -- довільні дані події
    created_by    UUID         REFERENCES users(id),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

---

## V003 — Зміни

### `system_settings`
```sql
CREATE TABLE system_settings (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_time_start  TIME NOT NULL DEFAULT '07:00',
    work_time_end    TIME NOT NULL DEFAULT '22:00',
    updated_by       UUID REFERENCES users(id),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- завжди один рядок
```

### `shifts`
```sql
CREATE TABLE shifts (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shift_number          INTEGER       NOT NULL,
    generator_id          UUID          NOT NULL REFERENCES generators(id),
    started_by            UUID          REFERENCES users(id),
    started_at            TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    stopped_by            UUID          REFERENCES users(id),
    stopped_at            TIMESTAMPTZ,
    duration_minutes      DECIMAL(10,2),
    fuel_consumed_liters  DECIMAL(10,3),
    motohours_accumulated DECIMAL(10,2),
    status                VARCHAR(10)   NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE | CLOSED
    created_at            TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
```

---

## V004 — Паливо та Мастило

### `fuel_stock`
```sql
CREATE TABLE fuel_stock (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fuel_type             VARCHAR(20)   NOT NULL DEFAULT 'A95',
    current_liters        DECIMAL(10,2) NOT NULL DEFAULT 0,
    max_limit_liters      DECIMAL(10,2) NOT NULL DEFAULT 200,
    warning_level_liters  DECIMAL(10,2) NOT NULL DEFAULT 30,
    updated_at            TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
-- завжди один рядок
```

### `fuel_deliveries`
```sql
CREATE TABLE fuel_deliveries (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fuel_type         VARCHAR(20)   NOT NULL,
    liters            DECIMAL(10,2) NOT NULL,
    check_number      VARCHAR(50),
    delivered_by_name VARCHAR(100),
    accepted_by       UUID          REFERENCES users(id),
    stock_before      DECIMAL(10,2) NOT NULL,
    stock_after       DECIMAL(10,2) NOT NULL,
    delivered_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
```

### `fuel_refills`
```sql
CREATE TABLE fuel_refills (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generator_id     UUID          NOT NULL REFERENCES generators(id),
    performed_by     UUID          REFERENCES users(id),
    liters           DECIMAL(10,2) NOT NULL,
    tank_level_before DECIMAL(10,2) NOT NULL,
    tank_level_after  DECIMAL(10,2) NOT NULL,
    stock_before     DECIMAL(10,2) NOT NULL,
    stock_after      DECIMAL(10,2) NOT NULL,
    refilled_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
```

### `oil_stock`
```sql
CREATE TABLE oil_stock (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generator_id     UUID          NOT NULL REFERENCES generators(id),
    oil_type         VARCHAR(50)   NOT NULL,
    current_quantity DECIMAL(10,3) NOT NULL DEFAULT 0,
    unit             VARCHAR(5)    NOT NULL DEFAULT 'L',  -- L | KG
    updated_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
```

---

## V005 — Корекції та Графік

### `adjustments`
```sql
CREATE TABLE adjustments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    adjustment_type VARCHAR(30)   NOT NULL,  -- MOTOHOURS_ADJUST | FUEL_STOCK_ADJUST | ...
    entity_type     VARCHAR(30)   NOT NULL,
    entity_id       UUID,
    value_before    DECIMAL(12,3),
    value_after     DECIMAL(12,3),
    delta           DECIMAL(12,3),
    reason          TEXT          NOT NULL,
    performed_by    UUID          REFERENCES users(id),
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
```

### `outage_schedule`
```sql
CREATE TABLE outage_schedule (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outage_date  DATE        NOT NULL,
    hour_start   SMALLINT    NOT NULL,  -- 0–23
    hour_end     SMALLINT    NOT NULL,  -- 0–23
    note         TEXT,
    created_by   UUID        REFERENCES users(id),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Візуальна мапа зв'язків

```
roles ◄────────────────────────────────── users
                                           │
         ┌───────────────────────────────┤
         │                               │
    generators ◄───── generator_settings  (1:1)
         │
         ├──── motohours_log
         ├──── maintenance_log
         ├──── shifts ◄────────── users
         ├──── fuel_refills ◄───── users
         ├──── oil_stock
         └──── event_log ◄─────── users

fuel_stock (1 рядок)
 fuel_deliveries ◄──── users

outage_schedule ◄─── users
adjustments ◄────── users
```
