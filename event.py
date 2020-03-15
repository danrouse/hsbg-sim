from enum import Enum, auto


class Event(Enum):
    DEATHRATTLE = auto()
    OVERKILL = auto()

    DAMAGE_RECEIVED = auto()
    BEFORE_ATTACK = auto()
    COMBAT_START = auto()

    MINION_DIED = auto()
    FRIENDLY_MINION_SUMMONED = auto()
    FRIENDLY_MINION_LOST_DIVINE_SHIELD = auto()
