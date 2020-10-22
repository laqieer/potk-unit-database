# -*- coding: utf-8 -*-
from typing import Tuple, Dict

from .skills import SkillsRepo
from ..master_data import MasterDataRepo, MasterData
from ..model import UnitJob, JobCharacteristic, JobCharacteristicBonus, StatType

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


class JobsRepo:
    def __init__(self, repo: MasterDataRepo, skills: SkillsRepo):
        self._skills = skills
        self._job_characteristics: Dict[int, JobCharacteristic] = {
            js.ID: js
            for js in (
                self._create_job_skill(b)
                for b in repo.read(MasterData.JobCharacteristics)
            )
        }
        self._jobs: Dict[int, UnitJob] = {
            job.ID: job for job in (
                self._create_job(j) for j in repo.read(MasterData.UnitJob)
            )
        }

    def get_job(self, job_id: int) -> UnitJob:
        return self._jobs[job_id]

    def _create_job(self, job: dict) -> UnitJob:
        initials = {f'initial_{s.name.lower()}': job[s.ini_key]
                    for s in StatType}
        return UnitJob(
            ID=job['ID'],
            name=job['name'],
            movement=job['movement'],
            new_cost=job['new_cost'],
            characteristics=self._find_characteristics(
                job['job_characteristics_id']),
            **initials
        )

    def _find_characteristics(self, ids_str: str) -> Tuple[JobCharacteristic]:
        if not ids_str:
            return tuple()
        return tuple(
            self._job_characteristics[i]
            for i in (int(s) for s in ids_str.split(','))
            # Not every characteristic has a mastery bonus (e.g. terrain
            # passives); We need to skip these.
            if i in self._job_characteristics
        )

    def _create_job_skill(self, ch: dict) -> JobCharacteristic:
        return JobCharacteristic(
            ID=ch['ID'],
            # skill2, when present, is always a hidden stat buff passive.
            # But these are already mentioned in the first skill description.
            skill=self._skills.get_skill(ch['skill_BattleskillSkill']),
            bonuses=self._create_bonuses(ch)
        )

    @staticmethod
    def _create_bonuses(ch: dict) -> Tuple[JobCharacteristicBonus]:
        result = []
        for s in ('', 2, 3):
            raw_stat = ch[f'levelmax_bonus{s}_JobCharacteristicsLevelmaxBonus']
            plus_value = ch[f'levelmax_bonus_value{s}']
            stat = JOB_CH_BONUS_TO_STAT.get(raw_stat)
            result.append(JobCharacteristicBonus(stat, plus_value))
        return tuple(result)
