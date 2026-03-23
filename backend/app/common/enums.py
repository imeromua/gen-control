import enum


class RoleName(str, enum.Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"


class GeneratorType(str, enum.Enum):
    MAIN = "MAIN"
    BACKUP = "BACKUP"


class FuelType(str, enum.Enum):
    A92 = "A92"
    A95 = "A95"
    DIESEL = "DIESEL"
    GAS = "GAS"


class EventType(str, enum.Enum):
    GENERATOR_CREATED = "GENERATOR_CREATED"
    GENERATOR_SETTINGS_UPDATED = "GENERATOR_SETTINGS_UPDATED"
    GENERATOR_DEACTIVATED = "GENERATOR_DEACTIVATED"
    MAINTENANCE_PERFORMED = "MAINTENANCE_PERFORMED"
