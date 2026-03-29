from enum import StrEnum


class EventType(StrEnum):
    """
    Канонічний список типів подій для event_log.

    ЗАБОРОНЕНО використовувати рядкові літерали напряму.
    Завжди використовуй: EventType.SHIFT_STARTED тощо.

    Всі значення та структура meta описані в docs/EVENT_SCHEMA.md
    """

    SHIFT_STARTED = "SHIFT_STARTED"
    SHIFT_STOPPED = "SHIFT_STOPPED"
    FUEL_REFILL   = "FUEL_REFILL"
    FUEL_DELIVERY = "FUEL_DELIVERY"
