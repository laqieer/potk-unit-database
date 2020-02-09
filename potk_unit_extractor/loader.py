from potk_unit_extractor.model import *
from dataclasses import dataclass
import math


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
    source_unit: UnitData = None

    @property
    def id(self):
        return self.unit['ID']

    def type_data(self, unit_type: UnitType):
        return self.types[unit_type.value]


class Loader:
    """OOP Based loader for unit data based on raw lists-of-dicts.
    """
    def __init__(self, units, parameters, initials, jobs, types_data, evos):
        """
        :param units: List of unit info (UnitUnit).
        :param parameters: List of parameters info (UnitUnitParameter)
        :param initials: List of initial parameters (UnitInitialParam)
        :param jobs: List of jobs (UnitJob)
        :param types_data: List of param data by unit type (UnitTypeParameter)
        :param evos: List of evolution patterns (UnitEvolutionPattern)
        """
        # Converts the lists into dicts indexed by ID for fast access.
        self.units = {int(it['ID']): it for it in units}
        self.parameters = {int(it['ID']): it for it in parameters}
        self.initials = {int(it['ID']): it for it in initials}
        self.jobs = {int(it['ID']): it for it in jobs}
        # Type data is actually a two level index by rarity and typing.
        self.types_data = {}
        for data in types_data:
            rarity = data['rarity_UnitRarity']
            if rarity not in self.types_data:
                self.types_data[rarity] = {}
            type_ = data['unit_type_UnitType']
            self.types_data[rarity][type_] = data
        # Evolutions are reverse-mapped for evo bonus lookup.
        self.evos = {int(it['target_unit_UnitUnit']): it for it in evos}

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
            })
        return raw

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

        same_ch_id = data.unit['same_character_id']
        jp_name: str = data.unit['name']
        eng_name: str = data.unit['english_name']
        level: Level = self._load_level(data.params)
        stats: UnitStats = self._load_unit_stats(data)
        return UnitData(unit_id, same_ch_id, jp_name, eng_name, level, stats)

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
        return Stat(
            initial=ini, evo_bonus=evo, growth=gr, compose=compose, ud=0)

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

    def _raw_unit(self, unit_id: int) -> _RawUnitData:
        """
        Composes all raw data relevant for an unit.

        :param unit_id: Desired unit ID.
        :return: Raw data for the unit.
        """
        unit = self.units[unit_id]
        return _RawUnitData(
            unit=unit,
            params=self.parameters[unit['parameter_data_UnitUnitParameter']],
            initial=self.initials[unit_id],
            job=self.jobs[unit['job_UnitJob']],
            types=self.types_data[unit['rarity_UnitRarity']],
            evo_from=self.evos[unit_id] if unit_id in self.evos else None
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
