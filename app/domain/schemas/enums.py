from enum import Enum


class ResourceType(str, Enum):
    STATION = "station"
    CRAWLER = "crawler"
    PLATFORM = "platform"
    RT = "rt"
    OPERATOR = "operator"


class Sites(str, Enum):
    # Add your actual values here
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    CENTER = "CENTER"


class PlatformTypes(str, Enum):
    TYPE_A = "TYPE_A"
    TYPE_B = "TYPE_B"


class RtLocations(str, Enum):
    LOC_1 = "LOC_1"
    LOC_2 = "LOC_2"


class Sections(str, Enum):
    SECTION_A = "SECTION_A"
    SECTION_B = "SECTION_B"


class MissionTypes(str, Enum):
    TRAINING = "TRAINING"
    OPERATIONAL = "OPERATIONAL"


class MissionStatuses(str, Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MissionOrigins(str, Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"


class OperatorRolesEnum(str, Enum):
    COMMANDER = "COMMANDER"
    OPERATOR = "OPERATOR"
    TECHNICIAN = "TECHNICIAN"
