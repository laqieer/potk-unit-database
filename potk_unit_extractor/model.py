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


@dataclass
class UnitData:
    ID: int
    same_character_id: int
    resource_id: int
    jp_name: str
    eng_name: str
    level: Level
    stats: UnitStats
