from enum import StrEnum


class EventType(StrEnum):
    """Canonical event types for event_log.

    Usage:
        await event_log.write(event_type=EventType.SHIFT_STARTED, meta={...}, db=db)

    Never use raw string literals — always reference this enum.
    See docs/EVENT_SCHEMA.md for required meta fields per event type.
    """

    SHIFT_STARTED = "SHIFT_STARTED"
    SHIFT_STOPPED = "SHIFT_STOPPED"
    FUEL_REFILL   = "FUEL_REFILL"
    FUEL_DELIVERY = "FUEL_DELIVERY"
