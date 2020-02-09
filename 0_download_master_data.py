# -*- coding:utf-8 -*-
# Python script to download only the assets necessary to extract unit data
# (Stats caps, skills, etc).
#
# Takes the paths.json file as an argument.
# Saves all files to the current working directory.

from pathlib import Path
from potk_unit_extractor.api import Environment, download_asset_bundle
import json
import shutil


def main(paths_fp):
    print("Loading file: " + paths_fp)
    with open(paths_fp, mode='rb') as fd:
        paths = json.load(fd)
    print("File loaded successfully")
    asset_bundle: dict = paths['AssetBundle']
    env = Environment(True)
    target = Path('.', 'bundles')
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir()

    names = [
        'MasterData/BattleUnitLandformFootstep',
        'MasterData/BoostBonusUnitBuildup',
        'MasterData/BoostBonusUnitCompose',
        'MasterData/BoostBonusUnitTransmigrate',
        'MasterData/ComposeMaxUnityValueSetting',
        'MasterData/GearSpecificationOfEquipmentUnit',
        'MasterData/GuildEmblemUnit',
        'MasterData/p0/BattleUnitLandformFootstep',
        'MasterData/p0/GearSpecificationOfEquipmentUnit',
        'MasterData/p0/UnitBuildupMaterialPattern',
        'MasterData/p0/UnitCameraPattern',
        'MasterData/p0/UnitCharacter',
        'MasterData/p0/UnitEvolutionPattern',
        'MasterData/p0/UnitEvolutionUnit',
        'MasterData/p0/UnitGroup',
        'MasterData/p0/UnitGroupClothingCategory',
        'MasterData/p0/UnitGroupGenerationCategory',
        'MasterData/p0/UnitGroupLargeCategory',
        'MasterData/p0/UnitGroupSmallCategory',
        'MasterData/p0/UnitIllustPattern',
        'MasterData/p0/UnitJob',
        'MasterData/p0/UnitLevel',
        'MasterData/p0/UnitProficiency',
        'MasterData/p0/UnitProficiencyIncr',
        'MasterData/p0/UnitProficiencyLevel',
        'MasterData/p0/UnitRarity',
        'MasterData/p0/UnitSkill',
        'MasterData/p0/UnitSkillEvolution',
        'MasterData/p0/UnitTrustLevelMaterialPattern',
        'MasterData/p0/UnitUnit',
        'MasterData/p0/UnitUnitBuildupLimitRelease',
        'MasterData/p0/UnitUnitDescription',
        'MasterData/p0/UnitUnitFamily',
        'MasterData/p0/UnitUnitGearModelKind',
        'MasterData/p0/UnitUnitGrowth',
        'MasterData/p0/UnitUnitParameter',
        'MasterData/p0/UnitUnitSupplement',
        'MasterData/p0/UnitVoicePattern',
        'MasterData/GearKind',
        'MasterData/ShopTopUnit',
        'MasterData/UnitAffiliationIcon',
        'MasterData/UnitAwakeningEffect',
        'MasterData/UnitBreakThrough',
        'MasterData/UnitBuildupMaterialPattern',
        'MasterData/UnitCameraPattern',
        'MasterData/UnitCharacter',
        'MasterData/UnitCutinInfo',
        'MasterData/UnitEvolutionPattern',
        'MasterData/UnitEvolutionUnit',
        'MasterData/UnitExtensionStory',
        'MasterData/UnitFamilyValue',
        'MasterData/UnitFootstepType',
        'MasterData/UnitGenderText',
        'MasterData/UnitGroup',
        'MasterData/UnitGroupClothingCategory',
        'MasterData/UnitGroupGenerationCategory',
        'MasterData/UnitGroupLargeCategory',
        'MasterData/UnitGroupSmallCategory',
        'MasterData/UnitHomeVoicePattern',
        'MasterData/UnitIllustPattern',
        'MasterData/UnitInitialParam',
        'MasterData/UnitJob',
        'MasterData/UnitJobFamily',
        'MasterData/UnitJobRankName',
        'MasterData/UnitLeaderSkill',
        'MasterData/UnitLevel',
        'MasterData/UnitMaterialQuestInfo',
        'MasterData/UnitModel',
        'MasterData/UnitPickupSkill',
        'MasterData/UnitProficiency',
        'MasterData/UnitProficiencyIncr',
        'MasterData/UnitRarity',
        'MasterData/UnitRenderingPattern',
        'MasterData/UnitSkill',
        'MasterData/UnitSkillAwake',
        'MasterData/UnitSkillCharacterQuest',
        'MasterData/UnitSkillEvolution',
        'MasterData/UnitSkillGroup',
        'MasterData/UnitSkillHarmonyQuest',
        'MasterData/UnitSkillIntimate',
        'MasterData/UnitSkillLevelUpProbability',
        'MasterData/UnitSkillupSetting',
        'MasterData/UnitSkillupSkillGroupSetting',
        'MasterData/UnitTransmigrationMaterial',
        'MasterData/UnitTransmigrationPattern',
        'MasterData/UnitTrustLevelMaterialPattern',
        'MasterData/UnitTrustUpperLimitEffect',
        'MasterData/UnitType',
        'MasterData/UnitTypeDeck',
        'MasterData/UnitTypeParameter',
        'MasterData/UnitTypeTicket',
        'MasterData/UnitTypeTicketUnusable',
        'MasterData/UnitUnit',
        'MasterData/UnitUnitBuildupAmount',
        'MasterData/UnitUnitBuildupLimitRelease',
        'MasterData/UnitUnitDescription',
        'MasterData/UnitUnitFamily',
        'MasterData/UnitUnitGearModelKind',
        'MasterData/UnitUnitParameter',
        'MasterData/UnitUnitStory',
        'MasterData/UnitVoicePattern',
        'MasterData/UnityValueUpItemQuest',
        'MasterData/UnityValueUpPattern',
    ]
    for name in names:
        download_asset_bundle(env, asset_bundle[name], name, target)

    print('All files downloaded')


if __name__ == "__main__":
    import sys
    try:
        main(sys.argv[1])
    except ValueError as ex:
        print(ex, file=sys.stderr)
        exit(1)
