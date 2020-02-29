from dataclasses import dataclass
from .master_data_parsers import *


@dataclass
class MasterDataAsset:
    name: str
    parser: callable


KNOWN_MASTER_DATA = [
    MasterDataAsset("UnitUnit", parse_unit_unit),
    MasterDataAsset("UnitUnitParameter", parse_unit_parameters),
    MasterDataAsset("UnitInitialParam", parse_unit_initial_parameters),
    MasterDataAsset("UnitTypeParameter", parse_unit_type_parameter),
    MasterDataAsset("UnitJob", parse_unit_job),
    MasterDataAsset("UnitEvolutionPattern", parse_unit_evolution_pattern),
    MasterDataAsset("ComposeMaxUnityValueSetting", parse_unit_compose_setting),
    MasterDataAsset("UnitRarity", parse_unit_rarity),
    MasterDataAsset("GearKind", parse_gear_kind),
    MasterDataAsset("UnitSkill", parse_unit_skill),
    MasterDataAsset("UnitSkillCharacterQuest", parse_unit_cq),
    MasterDataAsset("UnitSkillIntimate", parse_unit_ts),
    MasterDataAsset("BattleskillSkill", parse_battle_skill),
    MasterDataAsset("JobChangePatterns", parse_job_change_pattern),
    MasterDataAsset("JobCharacteristics", parse_job_characteristics),
    MasterDataAsset("UnitGroup", parse_unit_group),
    MasterDataAsset("UnitGroupClothingCategory", parse_unit_group_category),
    MasterDataAsset("UnitGroupGenerationCategory", parse_unit_group_category),
    MasterDataAsset("UnitGroupLargeCategory", parse_unit_group_category),
    MasterDataAsset("UnitGroupSmallCategory", parse_unit_group_category),
]
