from enum import StrEnum


class EventType(StrEnum):
    """Canonical event types for event_log.

    ALWAYS use these constants — never raw string literals.
    Adding a new event type: add here AND update docs/EVENT_SCHEMA.md.
    """

    SHIFT_STARTED = "SHIFT_STARTED"
    SHIFT_STOPPED = "SHIFT_STOPPED"
    FUEL_REFILL   = "FUEL_REFILL"
    FUEL_DELIVERY = "FUEL_DELIVERY"
