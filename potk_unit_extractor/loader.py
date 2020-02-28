from .model import *
from .translations import TAGS
from typing import Optional, Set
from dataclasses import dataclass
from pathlib import Path
import math
import json

# From game. Yes, it's hardcoded there too.
ELEMENTAL_SKILLS_IDS = [
    490000010, 490000013, 490000015, 490000017, 490000019, 490000021, 490000173
]

# Based on JobCharacteristicsLevelmaxBonus Enum.
JOB_CH_BONUS_TO_STAT = {
    0: None,  # none
    1: StatType.HP,  # hp_add
    2: StatType.STR,  # strength_add
    3: StatType.MGC,  # intelligence_add
    4: StatType.GRD,  # vitality_add
    5: StatType.SPR,  # mind_add
    6: StatType.SPD,  # agility_add
    7: StatType.TEC,  # dexterity_add
    8: StatType.LCK,  # lucky_add
    9: None,  # movement_add
}

# From UnitGroup
GROUP_FIELD_TAG_KIND = {
    "group_large_category_id_UnitGroupLargeCategory":
        UnitTagKind.LARGE,
    "group_small_category_id_UnitGroupSmallCategory":
        UnitTagKind.SMALL,
    "group_clothing_category_id_UnitGroupClothingCategory":
        UnitTagKind.CLOTHING,
    "group_clothing_category_id_2_UnitGroupClothingCategory":
        UnitTagKind.CLOTHING,
    "group_generation_category_id_UnitGroupGenerationCategory":
        UnitTagKind.GENERATION,
}


@dataclass()
class _RawUnitData:
    """Internal use only.
    Raw container for unit-related data.
    """
    unit: dict
    params: dict
    initial: dict
    cc_pattern: dict
    types: dict
    evo_from: dict
    ud: dict
    skills_ids: list
    groups: dict
    source_unit: UnitData = None

    @property
    def id(self):
        return self.unit['ID']

    def type_data(self, unit_type: UnitType):
        return self.types[unit_type.value]

    def job_id(self, cc: ClassChangeType):
        if not self.cc_pattern:
            return 0
        return self.cc_pattern[f'job{cc.value}_UnitJob']


class Loader:
    """OOP Based loader for unit data based on raw lists-of-dicts.
    """

    def __init__(
            self,
            units: list,
            parameters: list,
            initials: list,
            jobs: list,
            types_data: list,
            evos: list,
            ud: list,
            unit_skill: list,
            skills: list,
            cc_patterns: list,
            job_characteristics: list,
            unit_groups: list,
            unit_groups_large: list,
            unit_groups_small: list,
            unit_groups_clothing: list,
            unit_groups_gen: list,
    ):
        """
        :param units: List of unit info (UnitUnit).
        :param parameters: List of parameters info (UnitUnitParameter)
        :param initials: List of initial parameters (UnitInitialParam)
        :param jobs: List of jobs (UnitJob)
        :param types_data: List of param data by unit type (UnitTypeParameter)
        :param evos: List of evolution patterns (UnitEvolutionPattern)
        :param ud: List of Unleashed Domain Data (ComposeMaxUnityValueSetting)
        :param unit_skill: List of Unit and Skills associations (UnitSkill)
        :param skills: List of Battle Skill data (BattleskillSkill)
        :param cc_patterns: List of Class Changes data (JobChangePatterns)
        :param job_characteristics: List of JobCharacteristics
        :param unit_groups: List of UnitGroup
        :param unit_groups_large: List of UnitGroupLargeCategory
        :param unit_groups_small: List of UnitGroupSmallCategory
        :param unit_groups_clothing: List of UnitGroupClothingCategory
        :param unit_groups_gen: List of UnitGroupGenerationCategory
        """
        # Converts the lists into dicts indexed by ID for fast access.
        self.units = _index('ID', units)
        self.parameters = _index('ID', parameters)
        self.initials = _index('ID', initials)
        self.jobs = _index('ID', jobs)
        # Type data is actually a two level index by rarity and typing.
        self.types_data = {}
        for data in types_data:
            rarity = data['rarity_UnitRarity']
            if rarity not in self.types_data:
                self.types_data[rarity] = {}
            type_ = data['unit_type_UnitType']
            self.types_data[rarity][type_] = data
        # Evolutions are reverse-mapped for evo bonus lookup.
        self.evos = _index('target_unit_UnitUnit', evos)
        self.ud = _index('ID', ud)
        self.unit_skill = _group_by('unit_UnitUnit', unit_skill)
        self.skills = _index('ID', skills)
        self.cc_patterns = _index('unit_UnitUnit', cc_patterns)
        self.job_characteristics = _index('ID', job_characteristics)
        self.unit_groups = _index('unit_id', unit_groups)
        self.groups = {
            UnitTagKind.LARGE:      _index('ID', unit_groups_large),
            UnitTagKind.SMALL:      _index('ID', unit_groups_small),
            UnitTagKind.CLOTHING:   _index('ID', unit_groups_clothing),
            UnitTagKind.GENERATION: _index('ID', unit_groups_gen),
        }

    def load_playable_units(self):
        """
        Loads all units with IsNormalUnit=True (game code).

        :return: Generator of all loaded units, in no particular order.
        """
        excludes = [
            range(700000, 999999),  # .     700k, OG Misc
            range(1000000, 1999999),  # .     1m, Earth Males
            range(2700000, 2999999),  # .     2m, PoL Misc
            range(3700000, 3999999),  # .     3m, LR Misc
            range(4700000, 4999999),  # .     4m, Extra Art Misc
            range(5700000, 5999999),  # .     5m, IN Misc
            range(7000000, 7999999),  # .     7m, Taga Enemies?
            range(10000000, 19999999),  # .  10m, Laev Enemies?
            range(30000000, 39999999),  # .  30m, Guild Structures
            range(70000000, 79999999),  # .  70m, Memories, Cards, etc
            range(80000000, 89999999),  # .  80m, Innocents
            range(700000000, 799999999),  # 700m, Male Memories
            range(800000000, 899999999),  # 800m, Male Innocents
        ]
        generator = (
            unit['ID'] for unit in self.units.values()
            if not any(unit['ID'] in r for r in excludes)
        )
        for unit_id in generator:
            unit = self.load_unit(unit_id)
            # Some weird tyr versions are mixed in the fatom range.
            if unit.element != Element.NONE:
                yield unit

    def load_unit(self, unit_id: int) -> UnitData:
        """
        Loads a single unit given their ID.

        All data is fully loaded and valid. Lower rarity versions of the same
        unit may be loaded as well for evo bonuses calculation.

        :param unit_id: ID of the unit to be loaded.
        :return: Loaded unit data.
        """
        data = self._raw_unit(unit_id)
        if data.evo_from:
            data.source_unit = self.load_unit(data.evo_from['unit_UnitUnit'])

        tags = sorted(self._load_tags(data))
        skills = sorted(self._load_skills(data.skills_ids))
        return UnitData(
            ID=unit_id,
            same_character_id=data.unit['same_character_id'],
            character_id=data.unit['character_UnitCharacter'],
            resource_id=data.unit['resource_reference_unit_id_UnitUnit'],
            jp_name=data.unit['name'],
            eng_name=data.unit['english_name'],
            element=_compute_element(skills),
            gear_kind=GearKind(data.unit['kind_GearKind']),
            level=_load_level(data.params),
            rarity=UnitRarityStars(data.unit['rarity_UnitRarity']),
            job=self._load_job(data.unit['job_UnitJob']),
            cost=data.unit['cost'],
            is_awakened=(1 == data.unit['awake_unit_flag']),
            stats=self._load_unit_stats(data),
            vertex0=self._load_unit_cc(data, ClassChangeType.NORMAL),
            vertex1=self._load_unit_cc(data, ClassChangeType.VERTEX1),
            vertex2=self._load_unit_cc(data, ClassChangeType.VERTEX2),
            vertex3=self._load_unit_cc(data, ClassChangeType.VERTEX3),
            tags=tags,
            skills=skills,
        )

    def _load_unit_cc(
            self,
            data: _RawUnitData,
            cc: ClassChangeType
    ) -> Optional[UnitCCInfo]:
        """
        Load class change info for a unit. Returns None if no such CC.

        :param data: Raw unit data.
        :param cc: Desired class change.
        :return: CC or None.
        """
        job_id = data.job_id(cc)
        if not job_id:
            return None
        job = self._load_job(job_id)
        if cc == ClassChangeType.VERTEX3:
            # Assume all units with cc3 have cc1 and cc2 as well.
            # Since unlocking cc3 requires mastering both cc1 and cc2,
            # this is a safe assumption at least for now.
            cc1 = self._load_job(data.job_id(ClassChangeType.VERTEX1))
            cc2 = self._load_job(data.job_id(ClassChangeType.VERTEX2))
            job.mastery_bonuses += cc1.mastery_bonuses + cc2.mastery_bonuses

        return UnitCCInfo(
            c_type=cc,
            job=job,
            stats=self._load_unit_stats(data, job)
        )

    def _load_unit_stats(
            self, data: _RawUnitData, job: UnitJob = None) -> UnitStats:
        """
        Load all stats for all types of a given unit.

        :param data: Raw unit data.
        :param job: Optional job data. Uses unit default if None.
        :return: UnitStats
        """
        if not job:
            job: UnitJob = self._load_job(data.unit['job_UnitJob'])
        stats = {
            t.name.lower(): _load_stats(data, job, t)
            for t in UnitType
        }
        return UnitStats(**stats)

    def _load_job(self, job_id: int) -> UnitJob:
        """
        Loads job information.

        :param job_id: ID of the job.
        :return: Job Info.
        """
        job = self.jobs[job_id]
        initials = {f'initial_{s.name.lower()}': job[s.ini_key]
                    for s in StatType}
        return UnitJob(
            ID=job['ID'],
            name=job['name'],
            movement=job['movement'],
            new_cost=job['new_cost'],
            mastery_bonuses=self._load_job_bonuses(job),
            **initials
        )

    def _load_job_bonuses(self, job: dict) -> List[UnitJobSkillMasterBonus]:
        ids_str = job['job_characteristics_id']
        if not ids_str:
            return []
        result = []
        chs = (self.job_characteristics[int(i)] for i in ids_str.split(','))
        for ch in chs:
            bonus = _parse_job_bonus(ch)
            if bonus:
                result.append(bonus)
        return result

    def _load_tags(self, data: _RawUnitData) -> Set[UnitTag]:
        r = {
            self._load_tag(tag_id=data.groups[field_name], tag_kind=kind)
            for field_name, kind in GROUP_FIELD_TAG_KIND.items()
        }
        return {r for r in r if r.desc_jp.name}

    def _load_tag(self, tag_id: int, tag_kind: UnitTagKind) -> UnitTag:
        data: dict = self.groups[tag_kind][tag_id]
        tag_id = data['ID']
        return UnitTag(
            ID=tag_id,
            kind=tag_kind,
            desc_jp=UnitTagDesc(
                name=data['name'],
                short_label_name=data['short_label_name'],
                description=data['description'],
            ),
            desc_en=TAGS.get((tag_kind, tag_id))
        )

    def _load_skills(self, skills: list) -> list:
        return [self._load_skill(i) for i in skills]

    def _load_skill(self, skill_id: int) -> Skill:
        skill = self.skills[skill_id]
        return Skill(
            type=SkillType(skill['skill_type_BattleskillSkillType']),
            ID=skill['ID'],
            jp_desc=SkillDesc(
                name=skill['name'],
                full=skill['description'],
                short=skill['shortDescription'],
            ),
            en_desc=None,
            element=Element(skill['element_CommonElement']),
            target=SkillTarget(skill['target_type_BattleskillTargetType']),
            genres=sorted(
                SkillGenre(skill[k])
                for k in ['genre1_BattleskillGenre', 'genre2_BattleskillGenre']
                if skill[k]
            ),
            use_count=skill['use_count'],
            cooldown_turns=skill['charge_turn'],
            max_lv=skill['upper_level'],
            resource_id=skill['resource_reference_id'],
        )

    def _raw_unit(self, unit_id: int) -> _RawUnitData:
        """
        Composes all raw data relevant for an unit.

        :param unit_id: Desired unit ID.
        :return: Raw data for the unit.
        """
        unit = self.units[unit_id]
        if unit_id in self.unit_skill:
            skills = [link['skill_BattleskillSkill']
                      for link in self.unit_skill[unit_id]]
        else:
            skills = []
        return _RawUnitData(
            unit=unit,
            params=self.parameters[unit['parameter_data_UnitUnitParameter']],
            initial=self.initials[unit_id],
            types=self.types_data[unit['rarity_UnitRarity']],
            cc_pattern=_get_or_def(self.cc_patterns, unit_id),
            evo_from=_get_or_def(self.evos, unit_id),
            ud=_get_or_def(self.ud, unit[
                'compose_max_unity_value_setting_id_ComposeMaxUnityValueSetting'
            ]),
            skills_ids=skills,
            groups=self.unit_groups[unit_id],
        )


def _compute_element(skills: List[Skill]) -> Element:
    for skill in skills:
        if skill.ID in ELEMENTAL_SKILLS_IDS:
            return skill.element
    return Element.NONE


def _load_stats(
        data: _RawUnitData, job: UnitJob, t: UnitType) -> Stats:
    """
    Load all stats for a given unit job and type.

    :param data: Raw unit data.
    :param job: Job data.
    :param t: UnitType
    :return: Stats
    """
    stats = {
        stat.name.lower(): _load_stat(data, job, stat, t)
        for stat in StatType
    }
    return Stats(**stats)


def _load_stat(
        data: _RawUnitData,
        job: UnitJob,
        stat: StatType,
        t: UnitType) -> Stat:
    """
    Loads a single stat based on raw unit data, job and type.

    Performs the actual calculations to determine all components of a stat.
    This involves the unit current job and recursive info from previous
    versions (evolutions) to determine evo bonus.

    :param data: Raw unit data.
    :param job: Job data.
    :param stat: The stat type to be loaded.
    :param t: The unit type for adjusting caps and compose (fusion) values.
    :return: A single stat of the unit.
    """
    type_data = data.type_data(t)
    is_awake = 1 == data.unit['awake_unit_flag']

    return Stat(
        initial=data.initial[stat.ini_key] + job.get_initial(stat),
        evo_bonus=_calc_evo_bonus(data.source_unit, stat, t, is_awake),
        growth=_calc_gr(
            data.params[stat.max_key], type_data[stat.correction_key]),
        compose=type_data[stat.compose_key],
        ud=_load_ud(data.ud[stat.ud_key]),
        skill_master=job.get_skill_master_bonus(stat),
    )


def _parse_job_bonus(ch: dict) -> Optional[UnitJobSkillMasterBonus]:
    raw_stat = ch['levelmax_bonus_JobCharacteristicsLevelmaxBonus']
    stat = _get_or_def(JOB_CH_BONUS_TO_STAT, raw_stat)
    if stat is None:
        return None
    return UnitJobSkillMasterBonus(
        stat=stat, plus_value=ch['levelmax_bonus_value'])


def _load_level(params: dict) -> Level:
    """
    Loads level cap information for an unit.

    :param params: Unit parameters raw data.
    :return: Level info.
    """
    ini: int = params['_initial_max_level']
    inc: int = params['_level_per_breakthrough']
    mlb_c: int = params['breakthrough_limit']
    return Level(ini=ini, inc=inc, mlb_c=mlb_c)


def _load_ud(ud_str: str) -> UD:
    if not ud_str:
        return UD([])
    return UD([int(ud) for ud in ud_str.split(',')])


def _calc_evo_bonus(
        unit: UnitData, stat: StatType, t: UnitType, for_awakened: bool) -> int:
    """Internal shortcut to calculate evo bonuses.

    Deal with the special case for base units and awakened units.

    :param unit: Source unit data.
    :param stat: Desired stat.
    :param t: Unit type.
    :return: Provided evo bonus value.
    """
    if not unit:
        return 0
    s = unit.stats.of(t).of(stat)
    return s.evo_bonus if for_awakened else s.provided_evo_bonus


def _get_or_def(src: dict, key: any, def_val: any = None) -> any:
    return src[key] if key in src else def_val


def load_folder(path: Path) -> Loader:
    """
    Loads unit data from a folder containing json files in a predefined
    structure.

    :param path: Path of the folder containing the files.
    :return: Populated loader.
    """
    return Loader(
        units=_load_file(path / 'UnitUnit.json'),
        parameters=_load_file(path / 'UnitUnitParameter.json'),
        initials=_load_file(path / 'UnitInitialParam.json'),
        jobs=_load_file(path / 'UnitJob.json'),
        types_data=_load_file(path / 'UnitTypeParameter.json'),
        evos=_load_file(path / 'UnitEvolutionPattern.json'),
        ud=_load_file(path / 'ComposeMaxUnityValueSetting.json'),
        unit_skill=_load_file(path / 'UnitSkill.json'),
        skills=_load_file(path / 'BattleskillSkill.json'),
        cc_patterns=_load_file(path / 'JobChangePatterns.json'),
        job_characteristics=_load_file(path / 'JobCharacteristics.json'),
        unit_groups=_load_file(path / 'UnitGroup.json'),
        unit_groups_large=_load_file(path / 'UnitGroupLargeCategory.json'),
        unit_groups_small=_load_file(path / 'UnitGroupSmallCategory.json'),
        unit_groups_clothing=_load_file(
            path / 'UnitGroupClothingCategory.json'),
        unit_groups_gen=_load_file(path / 'UnitGroupGenerationCategory.json'),
    )


def _load_file(fp: Path) -> any:
    with fp.open(mode='r', encoding='utf8') as fd:
        return json.load(fd)


def _index(key: any, items: list) -> dict:
    return {it[key]: it for it in items}


def _group_by(key: any, items: list) -> dict:
    result = {}
    for item in items:
        key_val = item[key]
        if key_val not in result:
            result[key_val] = [item]
        else:
            result[key_val].append(item)
    return result


def _calc_gr(base: int, adjust: float) -> int:
    """
    Magic adjustment formula provided by s4itox (The Guidelines),
    gleamed from Cathrach original status bot.
    """
    adjust = round(adjust * 10000) / 10000
    return math.floor(base * (1 + adjust))
