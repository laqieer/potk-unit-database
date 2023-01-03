from __future__ import annotations

import math
import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from enum import Enum, IntEnum, unique
from functools import lru_cache, cached_property
from itertools import chain
from typing import List, Optional, Dict, Tuple, Set

DV_CAP = 99
logger = logging.getLogger(__name__)


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

    def _pair(self, dv: int) -> Tuple[range, int]:
        for dv_range, bonus in self._total_by_dv.items():
            if dv in dv_range:
                return dv_range, bonus
        raise ValueError(dv)

    def bonus(self, dv: int) -> int:
        return self._pair(dv)[1]

    @property
    def max(self) -> int:
        return self.bonus(DV_CAP)

    @property
    def dv_for_cap(self) -> int:
        return self._pair(DV_CAP)[0].start


@dataclass(eq=True, frozen=True)
class Stat:
    """
    Representation of a stat such as HP, STR, etc.

    Encodes all components of the stat separately, and provides computed
    properties for totals and other interesting values.
    """
    base: int  # Base stat from the unit itself.
    job_initial: int  # Base value from the current unit job.
    evo_bonus: int  # Maximum obtainable bonus from the previous rarity.
    growth: int  # Maximum growth value from level up. May be impossible.
    compose: int  # Maximum fusion value without UD.
    ud: UD  # Extra fusion value obtained from max UD.
    skill_master: int  # Extra value from skill mastery.

    @property
    def initial(self) -> int:
        return self.base + self.job_initial

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


@dataclass(eq=True, frozen=True)
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

    @cached_property
    def ud_milestones(self) -> List[int]:
        result = set()
        for s in StatType:
            result = result | self.of(s).ud.inc_by_milestone.keys()
        return sorted(result)

    @cached_property
    def has_ud(self) -> bool:
        # 0 is false
        return any(self.of(s).ud.max for s in StatType)

    def with_job(self, job: UnitJob, *extra_mastery: UnitJob) -> Stats:
        """Recalculate these stats with a different base job."""
        jobs = [job] + list(extra_mastery)
        args = {}
        for s in StatType:
            src = self.of(s)
            args[s.name.lower()] = Stat(
                base=src.base,
                job_initial=job.get_initial(s),
                evo_bonus=src.evo_bonus,
                growth=src.growth,
                compose=src.compose,
                ud=src.ud,
                skill_master=sum(j.get_skill_master_bonus(s) for j in jobs),
            )
        return Stats(**args)


class UnitType(IntEnum):
    BAL = 1  # +lck
    VIT = 2  # +hp, -spd, -tec
    STR = 3  # +str, -grd
    MGC = 4  # +mgc, -spr
    GRD = 5  # +grd, +spr, -str, -mgc
    DEX = 6  # +spd, +tec, -grd, -spr

    @property
    def jp_ch(self) -> str:
        return {
            UnitType.BAL: '王',
            UnitType.VIT: '命',
            UnitType.STR: '攻',
            UnitType.MGC: '魔',
            UnitType.GRD: '守',
            UnitType.DEX: '匠',
        }[self]


@dataclass(eq=True, frozen=True)
class UnitStats:
    bal: Stats
    vit: Stats
    str: Stats
    mgc: Stats
    grd: Stats
    dex: Stats

    def of(self, t: UnitType) -> Stats:
        return getattr(self, t.name.lower())

    def with_job(self, job: UnitJob, *extra_mastery: UnitJob) -> UnitStats:
        """Recalculate these stats with a different base job."""
        return UnitStats(**{
            t.name.lower(): self.of(t).with_job(job, *extra_mastery)
            for t in UnitType
        })


@dataclass(eq=True, frozen=True)
class Level:
    ini: int
    inc: int
    mlb_c: int

    @cached_property
    def max(self) -> int:
        return self.ini + (self.inc * self.mlb_c)


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

    @cached_property
    def stars(self) -> str:
        return f'{self.stars_count}★'

    @cached_property
    def stars_count(self) -> int:
        if self == self.ONE:
            return 1
        elif self == self.TWO:
            return 2
        elif self == self.THREE:
            return 3
        elif self == self.FOUR:
            return 4
        elif self == self.FIVE:
            return 5
        elif self == self.SIX:
            return 6


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
    UNIQUE = 8
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
    UNKNOWN = -1
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
    CALL = 14
    SEA = 15


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


class SkillAwakeCategory(IntEnum):
    # 1 == NONE, NORMAL
    # 2 == DRESS. Whatever it is, no units seem to have it.
    TRUST = 3
    GENERIC_RS = 4
    CHAOS_RS = 5
    HARMONIA_RS = 6
    TREISEMA_RS = 7
    TYRHELM_RS = 8
    COMMAND_RS = 9
    INTEGRAL_GEAR = 10
    SCHOOL_GEAR = 11
    IMITATE_GEAR = 12
    FOURTH_RAGNAROK = 13

    @classmethod
    def all_gear_hack_skill(cls) -> Set[SkillAwakeCategory]:
        return {c for c in cls} - {cls.TRUST, cls.SCHOOL_GEAR}


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
    max_lv: int
    genres: Tuple[SkillGenre]
    target: Optional[SkillTarget]
    element: Element
    category: Optional[SkillAwakeCategory]
    use_count: int
    cooldown_turns: int
    max_use_per_quest: int
    min_range: int
    max_range: int
    weight: int
    power: int
    hp_cost: int
    resource_id: int

    @cached_property
    def unit_type(self) -> Optional[UnitType]:
        for t in UnitType:
            flag = f'{t.jp_ch}器'
            if flag in self.jp_desc.name:
                return t
        return None

    @cached_property
    def range(self) -> Optional[str]:
        if not self.min_range or not self.max_range:
            return None
        if self.min_range == self.max_range:
            return f'{self.min_range}'
        return f'{self.min_range}-{self.max_range}'


@dataclass(eq=True, frozen=True, order=True)
class SkillEvo:
    unit_id: int
    from_skill: Skill
    to_skill: Skill
    req_level: int


@dataclass(eq=True, frozen=True, order=True)
class OvkSkill:
    same_character_id: int
    skill: Skill
    req_dv: int


class UnitTagKind(IntEnum):
    LARGE = 1
    SMALL = 2
    CLOTHING = 3
    GENERATION = 4
    CUSTOM = 23999  # Does not exists in game


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

    @property
    def iid(self) -> Tuple[UnitTagKind, int]:
        return self.kind, self.ID


@unique
class CustomTags(Enum):
    """Custom Unit tags, Not actually tags in game"""
    AWAKENED = UnitTag(
        kind=UnitTagKind.CUSTOM,
        ID=1,
        # Abusing JP being relied on as default.
        desc_jp=UnitTagDesc(
            name="Awakened",
            short_label_name="Awakened",
            description="Awakened Units",
        ),
    )
    REVO_KILLERS = UnitTag(
        kind=UnitTagKind.CUSTOM,
        ID=2,
        desc_jp=UnitTagDesc(
            name="Revolutionary Killers",
            short_label_name="Revo",
            description="Any Saint / Karma / Order Killers",
        ),
    )
    MALE_KILLERS = UnitTag(
        kind=UnitTagKind.CUSTOM,
        ID=3,
        desc_jp=UnitTagDesc(
            name="Male Killers",
            short_label_name="Male",
            description="Also known as Killer Princes.",
        ),
    )


@dataclass(eq=True, frozen=True)
class JobCharacteristicBonus:
    stat: StatType
    plus_value: int


@dataclass(eq=True, frozen=True)
class JobCharacteristic:
    ID: int
    skill: Skill
    bonuses: Tuple[JobCharacteristicBonus]


@dataclass(eq=True, frozen=True)
class UnitJob:
    ID: int
    name: str
    movement: int
    characteristics: Tuple[JobCharacteristic]
    initial_hp: int
    initial_str: int
    initial_mgc: int
    initial_grd: int
    initial_spr: int
    initial_spd: int
    initial_tec: int
    initial_lck: int
    new_cost: int

    @cached_property
    def skills(self) -> Tuple[Skill]:
        return tuple(c.skill for c in self.characteristics)

    def get_initial(self, stat_type: StatType) -> int:
        return getattr(self, 'initial_' + stat_type.name.lower())

    @lru_cache(maxsize=None)
    def get_skill_master_bonus(self, stat_type: StatType) -> int:
        return sum(mb.plus_value
                   for ch in self.characteristics
                   for mb in ch.bonuses
                   if mb.stat == stat_type)


class ClassChangeType(IntEnum):
    NORMAL = 1
    VERTEX1 = 2
    VERTEX2 = 3
    VERTEX3 = 4
    VERTEX4 = 5
    VERTEX5 = 6
    VERTEX6 = 7


@dataclass(eq=True, frozen=True)
class UnitSkills:
    relationship: Optional[Skill]
    leader: Optional[Skill]
    intimate: Optional[Skill]  # Multi DS
    harmony: Optional[Skill]  # Multi DS that requires CQ.
    types: Dict[UnitType, Tuple[Skill]]
    evolutions: Dict[Skill, SkillEvo]
    cq: Tuple[Skill]
    native: Tuple[Skill]
    ovk: Optional[OvkSkill]

    @cached_property
    def basic(self) -> Tuple[Skill]:
        return tuple(chain(iter(self.cq), iter(self.native)))

    @cached_property
    def multi_skill(self) -> Optional[Skill]:
        return self.intimate or self.harmony


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
    can_equip_all_rs: bool
    stats: UnitStats
    cc: Dict[ClassChangeType, UnitJob]
    tags: Tuple[UnitTag]
    skills: UnitSkills
    published_at: date
    evolved_from: Optional[UnitData]
    can_evolve: bool
    _cache: dict = field(init=False, default_factory=dict)

    @cached_property
    def any_name(self) -> str:
        return self.eng_name if self.eng_name else self.jp_name

    @cached_property
    def h_id(self) -> str:
        tags = ', '.join(t.desc.short_label_name for t in self.tags if t.desc.name)
        return f'<{self.ID} {self.rarity.stars} {self.any_name} ({tags})>'

    @cached_property
    def short_title(self) -> str:
        return f'{self.rarity.stars} {self.any_name} ({self.element.name}) ' \
               f'[{self.ID}]'

    @cached_property
    def qualifier(self) -> str:
        if self.is_awakened:
            return self.rarity.stars + ' Awakened'
        elif self.evolved_from and self.rarity == self.evolved_from.rarity:
            return self.rarity.stars + '+'
        else:
            return self.rarity.stars

    @cached_property
    def has_ud(self) -> bool:
        # UD isn't affected by unit type.
        return self.stats.bal.has_ud

    def cc_stats(self, cc_type: ClassChangeType) -> UnitStats:
        if cc_type in self._cache:
            return self._cache[cc_type]

        if cc_type == ClassChangeType.NORMAL:
            return self.stats

        job = self.cc[cc_type]  # Possible KeyError is intentional.
        extra = []
        if cc_type == ClassChangeType.VERTEX3:
            # Assume all units with cc3 have cc1 and cc2 as well.
            # Since unlocking cc3 requires mastering both cc1 and cc2,
            # this is a safe assumption at least for now.
            extra = [
                self.cc[ClassChangeType.VERTEX1],
                self.cc[ClassChangeType.VERTEX2]
            ]
        self._cache[cc_type] = self.stats.with_job(job, *extra)
        return self._cache[cc_type]

    @cached_property
    def sorted_vertex(self) -> Tuple[Tuple[ClassChangeType, UnitJob]]:
        return tuple(sorted(
            (ct, j) for ct, j in self.cc.items()
            if ct != ClassChangeType.NORMAL
        ))

    @cached_property
    def equipable_categories(self) -> Tuple[SkillAwakeCategory]:
        if not self.skills.relationship:
            # noinspection PyTypeChecker
            return ()

        cats: Set[SkillAwakeCategory] = set()
        if self.can_equip_all_rs:
            cats = cats | SkillAwakeCategory.all_gear_hack_skill()

        tags = {t.iid for t in self.tags}
        if (UnitTagKind.LARGE, 2) in tags:  # Gaku
            cats.add(SkillAwakeCategory.SCHOOL_GEAR)
        if (UnitTagKind.LARGE, 4) in tags:  # PoL
            cats.add(SkillAwakeCategory.TRUST)
        if {(UnitTagKind.LARGE, 5), (UnitTagKind.LARGE, 7)} & tags:  # LR/IN
            cats.add(SkillAwakeCategory.GENERIC_RS)
        if (UnitTagKind.SMALL, 10) in tags:
            cats.add(SkillAwakeCategory.HARMONIA_RS)
        if (UnitTagKind.SMALL, 11) in tags:
            cats.add(SkillAwakeCategory.CHAOS_RS)
        if (UnitTagKind.SMALL, 12) in tags:
            cats.add(SkillAwakeCategory.TREISEMA_RS)
        if (UnitTagKind.SMALL, 13) in tags:
            cats.add(SkillAwakeCategory.TYRHELM_RS)
        if (UnitTagKind.SMALL, 16) in tags:
            cats.add(SkillAwakeCategory.COMMAND_RS)
        if (UnitTagKind.SMALL, 17) in tags:
            cats.add(SkillAwakeCategory.INTEGRAL_GEAR)
        if (UnitTagKind.SMALL, 18) in tags:
            cats.add(SkillAwakeCategory.IMITATE_GEAR)

        # Silver tape to deal with SS LR, IN, etc.
        if SkillAwakeCategory.all_gear_hack_skill() & cats:
            cats.add(SkillAwakeCategory.GENERIC_RS)

        return tuple(sorted(cats))


def try_parse_skill_enum(output_type, source: dict, key, default=None, skip_if=None):
    value = source[key]
    if skip_if is not None and skip_if(value):
        return None
    try:
        return output_type(value)
    except ValueError:
        source_id = source.get('ID')
        logger.warning(
            "ignored unmapped %s for skill['ID']=%d (skill['%s']=%s)",
            str(output_type), source_id, str(key), str(value)
        )
        return default
