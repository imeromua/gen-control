from enum import StrEnum


class EventType(StrEnum):
    """Canonical enum for all event_log event_type values.

    Rules:
    - Always use this enum when writing to event_log.
    - Never pass raw strings like "SHIFT_STARTED" directly.
    - Adding a new event type here is the ONLY correct way to extend event_log.
    """

    SHIFT_STARTED = "SHIFT_STARTED"
    SHIFT_STOPPED = "SHIFT_STOPPED"

    FUEL_REFILL = "FUEL_REFILL"
    FUEL_DELIVERY = "FUEL_DELIVERY"

    OIL_ADDED = "OIL_ADDED"

    ADJUSTMENT = "ADJUSTMENT"

    OUTAGE_CREATED = "OUTAGE_CREATED"
    OUTAGE_UPDATED = "OUTAGE_UPDATED"
