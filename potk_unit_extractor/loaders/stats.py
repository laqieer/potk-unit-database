# -*- coding: utf-8 -*-
import math
from functools import lru_cache
from typing import Dict

from . import UnitMetadata
from .jobs import JobsRepo
from ..master_data import MasterDataRepo, MasterData
from ..model import UnitStats, Stat, StatType, UnitType, UD, Stats, Level


class StatsRepo:
    def __init__(self, repo: MasterDataRepo, jobs: JobsRepo):
        self._jobs = jobs
        self._units: Dict[int, UnitMetadata] = {
            u.ID: u
            for u in map(UnitMetadata, repo.read(MasterData.UnitUnit))
        }
        self._parameters = repo.index(
            key='ID', res=MasterData.UnitUnitParameter)
        self._initials = repo.index(
            key='ID', res=MasterData.UnitInitialParam)
        self._types_data = repo.nested_index(
            k1='rarity_UnitRarity', k2='unit_type_UnitType',
            res=MasterData.UnitTypeParameter)
        # Evolutions are reverse-mapped for evo bonus lookup.
        self._evo_patterns = {
            p['target_unit_UnitUnit']: p['unit_UnitUnit']
            for p in repo.read(MasterData.UnitEvolutionPattern)
        }
        self._ud = repo.index(
            key='ID', res=MasterData.ComposeMaxUnityValueSetting)

    @lru_cache(maxsize=None)
    def load_level(self, unit_id: int) -> Level:
        params = self._parameters[unit_id]
        return Level(
            ini=params['_initial_max_level'],
            inc=params['_level_per_breakthrough'],
            mlb_c=params['breakthrough_limit'],
        )

    @lru_cache(maxsize=None)
    def load_stats(self, unit_id: int) -> UnitStats:
        stats = {
            t.name.lower(): self._load_stats_of_type(unit_id, t)
            for t in UnitType
        }
        return UnitStats(**stats)

    def _load_stats_of_type(self, unit_id: int, ut: UnitType) -> Stats:
        stats = {
            stat.name.lower(): self._load_stat(unit_id, stat, ut)
            for stat in StatType
        }
        return Stats(**stats)

    @lru_cache(maxsize=None)
    def _load_stat(self, unit_id: int, st: StatType, ut: UnitType) -> Stat:
        unit = self._units[unit_id]
        type_data = self._types_data[unit.rarity][ut]
        job = self._jobs.get_job(unit.job_id)
        return Stat(
            base=self._initials[unit_id][st.ini_key],
            job_initial=job.get_initial(st),
            evo_bonus=self._calc_evo_bonus(unit, st, ut),
            growth=self._calc_gr(
                self._parameters[unit.ID][st.max_key],
                type_data[st.correction_key]
            ),
            compose=type_data[st.compose_key],
            ud=self._get_ud(unit.ud_id, st),
            skill_master=job.get_skill_master_bonus(st),
        )

    def _calc_evo_bonus(
            self, unit: UnitMetadata, st: StatType, ut: UnitType) -> int:
        prev_unit = self._evo_patterns.get(unit.ID)
        if not prev_unit:
            return 0
        s = self._load_stat(prev_unit, st, ut)
        return s.evo_bonus if unit.is_awake else s.provided_evo_bonus

    def _get_ud(self, ud_id: int, st: StatType) -> UD:
        ud_str = self._ud[ud_id][st.ud_key] if ud_id else None
        if not ud_str:
            return UD([])
        return UD([int(ud) for ud in ud_str.split(',')])

    @staticmethod
    def _calc_gr(base: int, adjust: float) -> int:
        """
        Magic adjustment formula provided by s4itox (The Guidelines),
        gleamed from Cathrach original status bot.
        """
        adjust = round(adjust * 10000) / 10000
        return math.floor(base * (1 + adjust))
