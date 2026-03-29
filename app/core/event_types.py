from enum import StrEnum


class EventType(StrEnum):
    SHIFT_STARTED  = "SHIFT_STARTED"
    SHIFT_STOPPED  = "SHIFT_STOPPED"
    FUEL_REFILL    = "FUEL_REFILL"
    FUEL_DELIVERY  = "FUEL_DELIVERY"
