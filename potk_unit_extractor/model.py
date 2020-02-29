from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import List, Optional
import math


DV_CAP = 99


class UD:
    """
    Representation for Unleashed Domain bonuses (Dupe Value status bonuses).

    Encodes the DV->Bonus series and allows quick access to the maximum value.
    Represents the bonuses for a single stat.
    """
    def __init__(self, dvs: List[int]):
        # This is a map of total_dv -> status_increase.
        self.inc_by_milestone = Counter(dvs)
        # This is a map of dv_range -> total_status_increase.
        # Please tell me a more clean way of doing this.
        self._total_by_dv = {}
        dvs = sorted({0, DV_CAP + 1} | set(self.inc_by_milestone.keys()))
        total = 0
        for prev, curr in zip(dvs, dvs[1:]):
            dv_range = range(prev, curr)
            self._total_by_dv[dv_range] = total
            total += self.inc_by_milestone[curr]

    def _pair(self, dv):
        for dv_range, bonus in self._total_by_dv.items():
            if dv in dv_range:
                return dv_range, bonus
        raise ValueError(dv)

    def bonus(self, dv):
        return self._pair(dv)[1]

    @property
    def max(self):
        return self.bonus(DV_CAP)

    @property
    def dv_for_cap(self):
        return self._pair(DV_CAP)[0].start


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
    ud: UD  # Extra fusion value obtained from max UD.
    skill_master: int  # Extra value from skill mastery.

    @property
    def max(self) -> int:
        return (self.initial
                + self.evo_bonus
                + self.growth
                + self.compose
                + self.ud.max
                + self.skill_master)

    @property
    def provided_evo_bonus(self) -> int:
        return math.ceil(self.max / 10)


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

    @property
    def ud_milestones(self) -> List[int]:
        result = set()
        for s in StatType:
            result = result | self.of(s).ud.inc_by_milestone.keys()
        return sorted(result)

    @property
    def has_ud(self) -> bool:
        # 0 is false
        return any(self.of(s).ud.max for s in StatType)


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

    @property
    def stars(self) -> str:
        if self == self.ONE:
            return '1★'
        elif self == self.TWO:
            return '2★'
        elif self == self.THREE:
            return '3★'
        elif self == self.FOUR:
            return '4★'
        elif self == self.FIVE:
            return '5★'
        elif self == self.SIX:
            return '6★'


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


class SkillType(IntEnum):
    """From MasterDataTable.BattleskillSkillType enum"""
    COMMAND = 1
    RELEASE = 2
    PASSIVE = 3
    DUEL = 4
    MAGIC = 5
    LEADER = 6
    ITEM = 7
    ENEMY = 8
    AILMENT = 9
    GROWTH = 10
    ATTACK_CLASS = 11
    ATTACK_ELEMENT = 12
    ATTACK_METHOD = 13


class SkillGenre(IntEnum):
    """From MasterDataTable.BattleskillGenre enum"""
    ATTACK = 1
    HEAL = 2
    BUFF = 3
    DEBUFF = 4
    AILMENT = 5
    DEFENSE = 6
    GROWTH = 7
    MOVE = 8


class SkillTarget(IntEnum):
    """From MasterDataTable.BattleskillTargetType enum"""
    MYSELF = 1
    PLAYER_RANGE = 2
    PLAYER_SINGLE = 3
    ENEMY_SINGLE = 4
    ENEMY_RANGE = 5
    DEAD_PLAYER_SINGLE = 6
    COMPLEX_SINGLE = 7
    COMPLEX_RANGE = 8
    PANEL_SINGLE = 9


@dataclass(eq=True, frozen=True, order=True)
class SkillDesc:
    name: str
    full: str
    short: str


@dataclass(eq=True, frozen=True, order=True)
class Skill:
    type: SkillType
    ID: int
    jp_desc: SkillDesc
    en_desc: Optional[SkillDesc]
    element: Element
    target: SkillTarget
    genres: List[SkillGenre]
    use_count: int
    cooldown_turns: int
    max_lv: int
    resource_id: int
    evo: Optional[SkillEvo]

    @property
    def skill_icon(self) -> Optional[str]:
        # TODO Handle CC skills?
        if self.type == SkillType.LEADER:
            return 'leader'
        elif self.type == SkillType.ITEM:
            return 'supply'
        elif self.type == SkillType.MAGIC:
            # TODO Use bullet icons
            return None
        else:
            rid = self.resource_id or self.ID
            return f'{rid}'


@dataclass(eq=True, frozen=True, order=True)
class SkillEvo:
    to_skill: Skill
    req_level: int


class UnitTagKind(IntEnum):
    LARGE = 1
    SMALL = 2
    CLOTHING = 3
    GENERATION = 4


@dataclass(eq=True, frozen=True, order=True)
class UnitTagDesc:
    name: str
    short_label_name: str
    description: str


@dataclass(eq=True, frozen=True, order=True)
class UnitTag:
    kind: UnitTagKind
    ID: int
    desc_jp: UnitTagDesc
    desc_en: UnitTagDesc = None

    @property
    def desc(self) -> UnitTagDesc:
        return self.desc_en or self.desc_jp

    @property
    def uid(self) -> str:
        return f'{self.kind.value}-{self.ID}'


@dataclass
class UnitJobSkillMasterBonus:
    stat: StatType
    plus_value: int


@dataclass
class UnitJob:
    ID: int
    name: str
    movement: int
    mastery_bonuses: List[UnitJobSkillMasterBonus]
    initial_hp: int
    initial_str: int
    initial_mgc: int
    initial_grd: int
    initial_spr: int
    initial_spd: int
    initial_tec: int
    initial_lck: int
    new_cost: int = 0

    def get_initial(self, stat_type: StatType) -> int:
        return getattr(self, 'initial_' + stat_type.name.lower())

    def get_skill_master_bonus(self, stat_type: StatType) -> int:
        return sum(mb.plus_value
                   for mb in self.mastery_bonuses
                   if mb.stat == stat_type)


class ClassChangeType(IntEnum):
    NORMAL = 1
    VERTEX1 = 2
    VERTEX2 = 3
    VERTEX3 = 4


@dataclass
class UnitCCInfo:
    c_type: ClassChangeType
    job: UnitJob
    stats: UnitStats


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
    is_awakened: bool
    stats: UnitStats
    vertex0: UnitCCInfo
    vertex1: UnitCCInfo
    vertex2: UnitCCInfo
    vertex3: UnitCCInfo
    tags: List[UnitTag]
    relationship_skill: Optional[Skill]
    leader_skill: Optional[Skill]
    intimate_skill: Optional[Skill]
    skills: List[Skill]

    @property
    def any_name(self) -> str:
        return self.eng_name if self.eng_name else self.jp_name

    @property
    def h_id(self) -> str:
        return f'<{self.ID} {self.rarity.stars} {self.any_name}>'

    @property
    def short_title(self) -> str:
        return f'{self.rarity.stars} {self.any_name} ({self.element.name}) ' \
               f'[{self.ID}]'

    @property
    def has_ud(self) -> bool:
        # UD isn't affected by unit type.
        return self.stats.bal.has_ud

    def get_cc(self, c_type: ClassChangeType) -> UnitCCInfo:
        return getattr(self, f'vertex{c_type.value - 1}')

    def has_cc(self, c_type: ClassChangeType = None) -> bool:
        if not c_type:
            return any(self.has_cc(c) for c in ClassChangeType)
        return self.get_cc(c_type) is not None
