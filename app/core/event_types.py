from enum import StrEnum


class EventType(StrEnum):
    """Canonical event types for event_log.

    Always use this enum — never hardcode string literals.
    Adding a new event type here is the ONLY place it needs to be defined.
    """

    SHIFT_STARTED = "SHIFT_STARTED"
    SHIFT_STOPPED = "SHIFT_STOPPED"
    FUEL_REFILL = "FUEL_REFILL"
    FUEL_DELIVERY = "FUEL_DELIVERY"
