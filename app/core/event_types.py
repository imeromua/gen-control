from enum import StrEnum


class EventType(StrEnum):
    """Canonical event types for event_log.

    IMPORTANT: Always use this enum — never raw string literals.
    All event_log entries must use one of these values.
    """

    SHIFT_STARTED = "SHIFT_STARTED"
    SHIFT_STOPPED = "SHIFT_STOPPED"
    FUEL_REFILL   = "FUEL_REFILL"
    FUEL_DELIVERY = "FUEL_DELIVERY"
