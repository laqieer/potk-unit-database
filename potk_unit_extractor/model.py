from dataclasses import dataclass
from enum import Enum, IntEnum
import math


@dataclass
class Stat:
    """
    Representation of a stat such as HP, STR, etc.

    Encodes all components of the stat separately, and provides computed
    properties for totals and other interesting values.
    """
    initial: int  # Base stat value at level 1.
    evo_bonus: int  # Maximum obtainable bonus from the previous rarity.
    growth: int  # Maximum growth value from level up. May be impossible.
    compose: int  # Maximum fusion value without UD.
    ud: int  # Extra fusion value obtained from max UD.

    @property
    def max(self) -> int:
        return self.initial \
               + self.evo_bonus \
               + self.growth \
               + self.compose \
               + self.ud

    @property
    def provided_evo_bonus(self) -> int:
        return math.ceil(self.max / 10)

    def __repr__(self) -> str:
        return str(self.max)


class StatType(Enum):
    HP = 'hp'
    STR = 'strength'
    MGC = 'intelligence'
    GRD = 'vitality'
    SPR = 'mind'
    SPD = 'agility'
    TEC = 'dexterity'
    LCK = 'lucky'

    @property
    def ini_key(self) -> str:
        return self.value + '_initial'

    @property
    def max_key(self) -> str:
        return self.value + '_max'

    @property
    def compose_key(self) -> str:
        return self.value + '_compose_max'

    @property
    def correction_key(self) -> str:
        return self.value + '_levelup_max_correction'

    @property
    def ud_key(self) -> str:
        return self.value + '_compose_add_max'


@dataclass
class Stats:
    hp: Stat
    str: Stat
    mgc: Stat
    grd: Stat
    spr: Stat
    spd: Stat
    tec: Stat
    lck: Stat

    def of(self, t: StatType) -> Stat:
        return getattr(self, t.name.lower())


class UnitType(IntEnum):
    BAL = 1  # +lck
    VIT = 2  # +hp, -spd, -tec
    STR = 3  # +str, -grd
    MGC = 4  # +mgc, -spr
    GRD = 5  # +grd, +spr, -str, -mgc
    DEX = 6  # +spd, +tec, -grd, -spr


@dataclass
class UnitStats:
    bal: Stats
    vit: Stats
    str: Stats
    mgc: Stats
    grd: Stats
    dex: Stats

    def of(self, t: UnitType) -> Stats:
        return getattr(self, t.name.lower())


@dataclass
class Level:
    ini: int
    inc: int
    mlb_c: int

    @property
    def max(self):
        return self.ini + (self.inc * self.mlb_c)

    def __repr__(self) -> str:
        return f'{self.ini}-{self.max}'


class UnitRarityStars(IntEnum):
    """Dirty shortcut to deal with unit rarities.
    For whatever reason they're loaded as entities with IDs all over the place,
    but in fact they're only 6 values, from 1-6 starts.

    This may come back to bite us if new unit rarities are added to the game.
    """
    ONE = 138
    TWO = 167
    THREE = 383
    FOUR = 642
    FIVE = 803
    SIX = 991


class GearKind(IntEnum):
    """Yet another dirty shortcut.
    This one actually maps to a Enum on the game side, so it's less risky.
    """
    SWORD = 1
    AXE = 2
    SPEAR = 3
    BOW = 4
    GUN = 5
    STAFF = 6
    SHIELD = 7
    UNIQUE_WEAPON = 8
    SMITH = 9
    ACCESSORIES = 10
    DRILLING = 11
    SPECIAL_DRILLING = 12
    SEA_PRESENT = 13
    MAGIC = 14
    DUMMY = 1001
    NONE = 9999


class Element(IntEnum):
    """List of all possible elements of a unit / skill.
    """
    NONE = 1
    FIRE = 2
    WIND = 3
    THUNDER = 4
    ICE = 5
    EARTH = 6
    LIGHT = 7
    DARK = 8
    # ??? Monster Elements?
    SAINT = 9
    DEMON = 10
    DRAGON = 11
    ANGEL = 12
    DEVIL = 13
    BEAST = 14
    FAIRY = 15
    PRINCESS = 16


@dataclass
class UnitJob:
    ID: int
    name: str
    movement: int
    new_cost: int = 0


@dataclass
class UnitData:
    ID: int
    same_character_id: int  # Only the same for different rarities / artworks.
    character_id: int  # Same for different versions of the same character.
    resource_id: int
    jp_name: str
    eng_name: str
    element: Element
    gear_kind: GearKind
    level: Level
    rarity: UnitRarityStars
    job: UnitJob
    cost: int
    stats: UnitStats

    @property
    def any_name(self) -> str:
        return self.eng_name if self.eng_name else self.jp_name
