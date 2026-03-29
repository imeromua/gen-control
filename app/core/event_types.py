from enum import StrEnum


class EventType(StrEnum):
    """
    Канонічний перелік типів подій для event_log.

    Використовувати ТІЛЬКИ ці константи — ніяких рядків-літералів.
    Детальний опис кожного типу та структура meta: docs/EVENT_SCHEMA.md
    """

    SHIFT_STARTED = "SHIFT_STARTED"
    SHIFT_STOPPED = "SHIFT_STOPPED"
    FUEL_REFILL   = "FUEL_REFILL"
    FUEL_DELIVERY = "FUEL_DELIVERY"
