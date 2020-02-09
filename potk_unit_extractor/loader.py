import json

from potk_unit_extractor.model import *
from dataclasses import dataclass
from pathlib import Path
import math

# From game. Yes, it's hardcoded there too.
ELEMENTAL_SKILLS_IDS = [
    490000010, 490000013, 490000015, 490000017, 490000019, 490000021, 490000173
]


@dataclass()
class _RawUnitData:
    """Internal use only.
    Raw container for unit-related data.
    """
    unit: dict
    params: dict
    initial: dict
    job: dict
    types: dict
    evo_from: dict
    ud: dict
    skills: list
    source_unit: UnitData = None

    @property
    def id(self):
        return self.unit['ID']

    def type_data(self, unit_type: UnitType):
        return self.types[unit_type.value]

    def compute_element(self):
        for skill in self.skills:
            if skill['ID'] in ELEMENTAL_SKILLS_IDS:
                return Element(skill['element_CommonElement'])
        return Element.NONE


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
            skills: list
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

    def dump_raw(self) -> list:
        """
        Produces a raw, json-like representation of unit data, grouped by unit.

        Does not calculate stats maximums or evo bonuses.
        Unsuitable for anything but debug. Remove-me ASAP.

        :return: Raw internal data.
        """
        raw = []
        for unit_id in self.units.keys():
            data = self._raw_unit(unit_id)
            raw.append({
                'unit':       data.unit,
                'parameters': data.params,
                'initial':    data.initial,
                'job':        data.job,
                'types':      data.types,
                'evo_from':   data.evo_from,
                'ud':         data.ud,
            })
        return raw

    def load_normal_units(self):
        """
        Loads all units with IsNormalUnit=True (game code).

        :return: Generator of all loaded units, in no particular order.
        """
        check_keys = [
            'is_consume_only',
            'is_evolution_only',
            'skillup_type',
            'is_breakthrough_only',
            'is_buildup_only',
            'is_appendedskill_only',
            'is_unity_value_up',
        ]
        generator = (
            unit['ID'] for unit in self.units.values()
            # This will match all units the game considers normal units.
            # i.e. Ignores evo mats and similar.
            # It *does* include enemies and misc stuff like Black Jack Cards.
            # TODO Filter this list down to only playable units.
            if not any(unit[k] for k in check_keys)
        )
        for unit_id in generator:
            yield self.load_unit(unit_id)

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

        return UnitData(
            ID=unit_id,
            same_character_id=data.unit['same_character_id'],
            character_id=data.unit['character_UnitCharacter'],
            resource_id=data.unit['resource_reference_unit_id_UnitUnit'],
            jp_name=data.unit['name'],
            eng_name=data.unit['english_name'],
            element=data.compute_element(),
            gear_kind=GearKind(data.unit['kind_GearKind']),
            level=self._load_level(data.params),
            rarity=UnitRarityStars(data.unit['rarity_UnitRarity']),
            job=self._load_job(data.job),
            cost=data.unit['cost'],
            stats=self._load_unit_stats(data),
        )

    def _load_unit_stats(self, data: _RawUnitData) -> UnitStats:
        """
        Load all stats for all types of a given unit.

        :param data: Raw unit data.
        :return: UnitStats
        """
        stats = {
            t.name.lower():
                self._load_stats(data, t)
            for t in UnitType
        }
        return UnitStats(**stats)

    def _load_stats(self, data: _RawUnitData, t: UnitType) -> Stats:
        """
        Load all stats for a given unit type.

        :param data: Raw unit data.
        :param t: UnitType
        :return: Stats
        """
        stats = {
            stat.name.lower(): self._load_stat(data, stat, t)
            for stat in StatType
        }
        return Stats(**stats)

    @staticmethod
    def _load_stat(data: _RawUnitData, stat: StatType, t: UnitType) -> Stat:
        """
        Loads a single stat based on raw unit data and type.

        Performs the actual calculations to determine all components of a stat.
        This involves the unit current job and recursive info from previous
        versions (evolutions) to determine evo bonus.

        :param data: Raw unit data.
        :param stat: The stat type to be loaded.
        :param t: The unit type for adjusting caps and compose (fusion) values.
        :return: A single stat of the unit.
        """
        type_data = data.type_data(t)
        ini: int = data.initial[stat.ini_key] + data.job[stat.ini_key]
        gr: int = data.params[stat.max_key]
        # FIXME float problems may result in different values for some units!
        # Validate against all owned units? Crowd source?
        gr = gr + math.floor(gr * type_data[stat.correction_key])
        compose: int = type_data[stat.compose_key]
        evo: int = _calc_evo_bonus(data.source_unit, stat, t)
        ud_str: str = data.ud[stat.ud_key]
        ud: int = len(ud_str.split(',')) if len(ud_str) > 0 else 0
        return Stat(
            initial=ini, evo_bonus=evo, growth=gr, compose=compose, ud=ud)

    @staticmethod
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

    @staticmethod
    def _load_job(job: dict) -> UnitJob:
        """
        Loads job information.

        :param job: Job information raw data.
        :return: Job Info.
        """
        return UnitJob(
            ID=job['ID'],
            name=job['name'],
            movement=job['movement'],
            new_cost=job['new_cost'],
        )

    def _raw_unit(self, unit_id: int) -> _RawUnitData:
        """
        Composes all raw data relevant for an unit.

        :param unit_id: Desired unit ID.
        :return: Raw data for the unit.
        """
        unit = self.units[unit_id]
        if unit_id in self.unit_skill:
            skills = [self.skills[link['skill_BattleskillSkill']]
                      for link in self.unit_skill[unit_id]]
        else:
            skills = []
        return _RawUnitData(
            unit=unit,
            params=self.parameters[unit['parameter_data_UnitUnitParameter']],
            initial=self.initials[unit_id],
            job=self.jobs[unit['job_UnitJob']],
            types=self.types_data[unit['rarity_UnitRarity']],
            evo_from=_get_or_def(self.evos, unit_id),
            ud=_get_or_def(self.ud, unit[
                'compose_max_unity_value_setting_id_ComposeMaxUnityValueSetting'
            ]),
            skills=skills,
        )


def _calc_evo_bonus(unit: UnitData, stat: StatType, t: UnitType) -> int:
    """Internal shortcut to calculate evo bonuses.

    Deal with the special case for base units.

    :param unit: Source unit data.
    :param stat: Desired stat.
    :param t: Unit type.
    :return: Provided evo bonus value.
    """
    if not unit:
        return 0
    return unit.stats.of(t).of(stat).provided_evo_bonus


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
    )


def _load_file(fp: Path) -> list:
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
