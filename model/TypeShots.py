from enum import Enum, EnumMeta
import typing


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


# name = value
class TypeShot(Enum, metaclass=MetaEnum):
    ANGLE = "Camera Angle"
    LEVEL = "Camera Level"
    SCALE = "Shot Scale"


class AngleShot(Enum, metaclass=MetaEnum):
    OVERHEAD = "Overhead"
    HIGH = "High"
    DUTCH = "Dutch"
    NOANGLE = "No angle"
    LOW = "Low"


class LevelShot(Enum, metaclass=MetaEnum):
    AERIAL = "Aerial"
    EYE = "Eye"
    SHOULDER = "Shoulder"
    HIP = "Hip"
    KNEE = "Knee"
    GROUND = "Ground"


class ScaleShot(Enum, metaclass=MetaEnum):
    CLOSE = "Close-up"
    MEDIUM = "Medium"
    LONG = "Long"


JoinTypeShots = typing.Union[AngleShot, LevelShot, ScaleShot]
