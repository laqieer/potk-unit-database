from collections import defaultdict
from enum import Enum, unique, auto
from pathlib import Path

import unitypack

from .master_data_parsers import *


@unique
class MasterData(Enum):
    # Names are important and case-sensitive. Do not change.
    UnitUnit = (auto(), parse_unit_unit)
    UnitUnitParameter = (auto(), parse_unit_parameters)
    UnitInitialParam = (auto(), parse_unit_initial_parameters)
    UnitTypeParameter = (auto(), parse_unit_type_parameter)
    UnitJob = (auto(), parse_unit_job)
    UnitEvolutionPattern = (auto(), parse_unit_evolution_pattern)
    ComposeMaxUnityValueSetting = (auto(), parse_unit_compose_setting)
    UnitRarity = (auto(), parse_unit_rarity)
    GearKind = (auto(), parse_gear_kind)
    UnitSkill = (auto(), parse_unit_skill)
    UnitLeaderSkill = (auto(), parse_unit_skill_link)
    UnitSkillCharacterQuest = (auto(), parse_unit_cq)
    UnitSkillAwake = (auto(), parse_unit_rs)
    UnitSkillIntimate = (auto(), parse_unit_skill_link)
    UnitSkillEvolution = (auto(), parse_unit_skill_evo)
    BattleskillSkill = (auto(), parse_battle_skill)
    JobChangePatterns = (auto(), parse_job_change_pattern)
    JobCharacteristics = (auto(), parse_job_characteristics)
    UnitGroup = (auto(), parse_unit_group)
    UnitGroupClothingCategory = (auto(), parse_unit_group_category)
    UnitGroupGenerationCategory = (auto(), parse_unit_group_category)
    UnitGroupLargeCategory = (auto(), parse_unit_group_category)
    UnitGroupSmallCategory = (auto(), parse_unit_group_category)
    OverkillersSkillRelease = (auto(), parse_ovk_skill_release)

    def __init__(self, iid: int, parser: callable):
        self.iid = iid
        self.parser = parser


class MasterDataRepo:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(exist_ok=True)

    def path_of(self, res: MasterData) -> Path:
        return self.root / f'{res.name}.unity3d'

    def read(self, res: MasterData) -> list:
        """Read a resource content from the unity3d file"""
        res_path = self.path_of(res)
        with res_path.open(mode='rb') as fd:
            pack = unitypack.load(fd)
        raw = pack.assets[0].objects[2].read().script
        return MasterDataReader(raw).read_all(len(raw), res.parser)

    def index(self, key: str, res: MasterData) -> dict:
        return {it[key]: it for it in self.read(res)}

    def group_by(self, key: str, res: MasterData) -> dict:
        result = defaultdict(list)
        for item in self.read(res):
            result[item[key]].append(item)
        return result

    def index_f(self, key_func: callable, res: MasterData) -> dict:
        return {key_func(it): it for it in self.read(res)}

    def nested_index(self, k1: str, k2: str, res: MasterData) -> dict:
        result = defaultdict(dict)
        for item in self.read(res):
            v1 = item[k1]
            v2 = item[k2]
            result[v1][v2] = item
        return result
