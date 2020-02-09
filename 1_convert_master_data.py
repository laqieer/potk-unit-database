# -*- coding:utf-8 -*-
# Python script to parse asset bundles with PotK Unit data and convert
# those bundles into more friendly JSON files.

from potk_unit_extractor.master_data_reader import MasterDataReader
from pathlib import Path
import json
import unitypack  # Tested with UnityPack 0.9.0


def unit_data_to_list(raw_data: bytes):
    reader = MasterDataReader(raw_data)
    result = []
    while reader.buf.tell() < len(raw_data):
        # We must guarantee the order of the read calls.
        # noinspection PyDictCreation
        unit = {}
        unit['ID'] = reader.ReadInt()
        unit['name'] = reader.ReadString(True)
        unit['english_name'] = reader.ReadString(True)
        unit['parameter_data_UnitUnitParameter'] = reader.ReadInt()
        unit['etc_data_UnitUnitDescription'] = reader.ReadInt()
        unit['published_at'] = reader.ReadDateTimeOrNull()
        unit['same_character_id'] = reader.ReadInt()
        unit['character_UnitCharacter'] = reader.ReadInt()
        unit['resource_reference_unit_id_UnitUnit'] = reader.ReadInt()
        unit['model_reference_id'] = reader.ReadInt()
        unit['rarity_UnitRarity'] = reader.ReadInt()
        unit['cost'] = reader.ReadInt()
        unit['job_UnitJob'] = reader.ReadInt()
        unit['is_consume_only'] = reader.ReadInt()
        unit['is_evolution_only'] = reader.ReadInt()
        unit['skillup_type'] = reader.ReadInt()
        unit['is_breakthrough_only'] = reader.ReadInt()
        unit['is_buildup_only'] = reader.ReadInt()
        unit['kind_GearKind'] = reader.ReadInt()
        unit['history_group_number'] = reader.ReadInt()
        unit['_base_sell_price'] = reader.ReadInt()
        unit['initial_gear_GearGear'] = reader.ReadInt()
        unit['vehicle_model_name'] = reader.ReadStringOrNull(True)
        unit['equip_model_name'] = reader.ReadStringOrNull(True)
        unit['equip_model_b_name'] = reader.ReadStringOrNull(True)
        unit['field_normal_face_material_name'] = reader.ReadString(True)
        unit['field_gray_body_material_name'] = reader.ReadString(True)
        unit['field_gray_face_material_name'] = reader.ReadString(True)
        unit['field_gray_vehicle_material_name'] = reader.ReadString(True)
        unit['field_gray_equip_material_name'] = reader.ReadString(True)
        unit['field_gray_equip_b_material_name'] = reader.ReadString(True)
        unit['duel_model_scale'] = reader.ReadFloat()
        unit['field_model_scale'] = reader.ReadFloat()
        unit['duel_shadow_scale_x'] = reader.ReadFloat()
        unit['duel_shadow_scale_z'] = reader.ReadFloat()
        unit['footstep_type_UnitFootstepType'] = reader.ReadInt()
        unit['camera_pattern_UnitCameraPattern'] = reader.ReadInt()
        unit['illust_pattern_UnitIllustPattern'] = reader.ReadInt()
        unit['cutin_pattern_id'] = reader.ReadIntOrNull()
        unit['voice_pattern_id'] = reader.ReadInt()
        unit['non_disp_weapon'] = reader.ReadInt()
        unit['buildup_limit_release_id_UnitUnitBuildupLimitRelease'] \
            = reader.ReadInt()
        unit['rainbow_on'] = reader.ReadBool()
        unit['trust_target_flag'] = reader.ReadBool()
        unit['awake_unit_flag'] = reader.ReadBool()
        unit['can_awake_unit_flag'] = reader.ReadBool()
        unit['formal_name'] = reader.ReadStringOrNull(True)
        unit['country_attribute'] = reader.ReadIntOrNull()
        unit['inclusion_ip'] = reader.ReadIntOrNull()
        unit['magic_warrior_flag'] = reader.ReadBool()
        unit['awake_special_skill_category_id'] = reader.ReadIntOrNull()
        unit['compose_max_unity_value_setting_id_ComposeMaxUnityValueSetting'] \
            = reader.ReadInt()
        unit['is_appendedskill_only'] = reader.ReadBool()
        unit['is_unity_value_up'] = reader.ReadBool()
        unit['job_characteristics_levelup_pattern'] = reader.ReadBool()
        # Skip 5 unknown bytes on end of each record.
        # TODO Determine what those 5 bytes are and store them in JSON.
        reader.buf.read(5)
        result.append(unit)
    return result


def read_raw_asset_data(fp: Path):
    with fp.open(mode='rb') as fd:
        pack = unitypack.load(fd)
    return pack.assets[0].objects[2].read().script


if __name__ == "__main__":
    wd = Path('.')
    unit_data_path = wd.glob("MasterData_UnitUnit_*.unity3d").__next__()
    raw_unit_data = read_raw_asset_data(unit_data_path)
    unit_data = unit_data_to_list(raw_unit_data)
    with open('UnitUnit.json', mode='w', encoding='utf8') as fd:
        json.dump(unit_data, fd, indent='\t', ensure_ascii=False)
