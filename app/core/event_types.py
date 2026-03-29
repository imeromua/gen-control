from enum import StrEnum


class EventType(StrEnum):
    """Canonical event types for event_log.

    USAGE: Always use EventType.* — never raw string literals.
    See docs/EVENT_SCHEMA.md for full meta structure per event type.
    """

    SHIFT_STARTED = "SHIFT_STARTED"
    SHIFT_STOPPED = "SHIFT_STOPPED"
    FUEL_REFILL   = "FUEL_REFILL"
    FUEL_DELIVERY = "FUEL_DELIVERY"
