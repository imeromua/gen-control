from enum import StrEnum


class EventType(StrEnum):
    """Canonical event types for event_log.

    All business operations MUST use these constants.
    Never use raw strings for event_type.
    """

    SHIFT_STARTED = "SHIFT_STARTED"
    SHIFT_STOPPED = "SHIFT_STOPPED"
    FUEL_REFILL = "FUEL_REFILL"
    FUEL_DELIVERY = "FUEL_DELIVERY"
