# -*- coding: utf-8 -*-
from functools import lru_cache
from typing import Dict

from .jobs import JobsRepo
from ..master_data import MasterDataRepo, MasterData
from ..model import UnitJob, ClassChangeType


class CCRepo:
    def __init__(self, repo: MasterDataRepo, jobs_repo: JobsRepo):
        self._jobs = jobs_repo
        self._cc_patterns = repo.index(
            key='unit_UnitUnit', res=MasterData.JobChangePatterns)

    @lru_cache(maxsize=None)
    def unit_cc(self, unit_id: int) -> Dict[ClassChangeType, UnitJob]:
        if unit_id not in self._cc_patterns:
            return {}
        pattern = self._cc_patterns[unit_id]
        return {
            ct: self._jobs.get_job(pattern[f'job{ct.value}_UnitJob'])
            for ct in ClassChangeType
            if pattern[f'job{ct.value}_UnitJob']
        }
