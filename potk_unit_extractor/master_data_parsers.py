from potk_unit_extractor.master_data_reader import MasterDataReader


def parse_unit_unit(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['name'] = reader.ReadString(True)
    item['english_name'] = reader.ReadString(True)
    item['parameter_data_UnitUnitParameter'] = reader.ReadInt()
    item['etc_data_UnitUnitDescription'] = reader.ReadInt()
    item['published_at'] = reader.ReadDateTimeOrNull()
    item['same_character_id'] = reader.ReadInt()
    item['character_UnitCharacter'] = reader.ReadInt()
    item['resource_reference_unit_id_UnitUnit'] = reader.ReadInt()
    item['model_reference_id'] = reader.ReadInt()
    item['rarity_UnitRarity'] = reader.ReadInt()
    item['cost'] = reader.ReadInt()
    item['job_UnitJob'] = reader.ReadInt()
    item['is_consume_only'] = reader.ReadInt()
    item['is_evolution_only'] = reader.ReadInt()
    item['skillup_type'] = reader.ReadInt()
    item['is_breakthrough_only'] = reader.ReadInt()
    item['is_buildup_only'] = reader.ReadInt()
    item['kind_GearKind'] = reader.ReadInt()
    item['history_group_number'] = reader.ReadInt()
    item['_base_sell_price'] = reader.ReadInt()
    item['initial_gear_GearGear'] = reader.ReadInt()
    item['vehicle_model_name'] = reader.ReadStringOrNull(True)
    item['equip_model_name'] = reader.ReadStringOrNull(True)
    item['equip_model_b_name'] = reader.ReadStringOrNull(True)
    item['field_normal_face_material_name'] = reader.ReadString(True)
    item['field_gray_body_material_name'] = reader.ReadString(True)
    item['field_gray_face_material_name'] = reader.ReadString(True)
    item['field_gray_vehicle_material_name'] = reader.ReadString(True)
    item['field_gray_equip_material_name'] = reader.ReadString(True)
    item['field_gray_equip_b_material_name'] = reader.ReadString(True)
    item['duel_model_scale'] = reader.ReadFloat()
    item['field_model_scale'] = reader.ReadFloat()
    item['duel_shadow_scale_x'] = reader.ReadFloat()
    item['duel_shadow_scale_z'] = reader.ReadFloat()
    item['footstep_type_UnitFootstepType'] = reader.ReadInt()
    item['camera_pattern_UnitCameraPattern'] = reader.ReadInt()
    item['illust_pattern_UnitIllustPattern'] = reader.ReadInt()
    item['cutin_pattern_id'] = reader.ReadIntOrNull()
    item['voice_pattern_id'] = reader.ReadInt()
    item['non_disp_weapon'] = reader.ReadInt()
    item['buildup_limit_release_id_UnitUnitBuildupLimitRelease'] \
        = reader.ReadInt()
    item['rainbow_on'] = reader.ReadBool()
    item['trust_target_flag'] = reader.ReadBool()
    item['awake_unit_flag'] = reader.ReadBool()
    item['can_awake_unit_flag'] = reader.ReadBool()
    item['formal_name'] = reader.ReadStringOrNull(True)
    item['country_attribute'] = reader.ReadIntOrNull()
    item['inclusion_ip'] = reader.ReadIntOrNull()
    item['magic_warrior_flag'] = reader.ReadBool()
    item['awake_special_skill_category_id'] = reader.ReadIntOrNull()
    item['compose_max_unity_value_setting_id_ComposeMaxUnityValueSetting'] \
        = reader.ReadInt()
    item['is_appendedskill_only'] = reader.ReadBool()
    item['is_unity_value_up'] = reader.ReadBool()
    item['job_characteristics_levelup_pattern'] = reader.ReadBool()
    # Skip 5 unknown bytes on end of each record.
    # TODO Determine what those 5 bytes are and store them in JSON.
    reader.buf.read(5)


def parse_unit_parameters(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['_level_pattern_id'] = reader.ReadInt()
    item['_initial_max_level'] = reader.ReadInt()
    item['breakthrough_limit'] = reader.ReadInt()
    item['_level_per_breakthrough'] = reader.ReadInt()
    item['hp_max'] = reader.ReadInt()
    item['strength_max'] = reader.ReadInt()
    item['vitality_max'] = reader.ReadInt()
    item['intelligence_max'] = reader.ReadInt()
    item['mind_max'] = reader.ReadInt()
    item['agility_max'] = reader.ReadInt()
    item['dexterity_max'] = reader.ReadInt()
    item['lucky_max'] = reader.ReadInt()
    item['hp_initial'] = reader.ReadInt()
    item['strength_initial'] = reader.ReadInt()
    item['vitality_initial'] = reader.ReadInt()
    item['intelligence_initial'] = reader.ReadInt()
    item['mind_initial'] = reader.ReadInt()
    item['agility_initial'] = reader.ReadInt()
    item['dexterity_initial'] = reader.ReadInt()
    item['lucky_initial'] = reader.ReadInt()
    item['hp_compose'] = reader.ReadInt()
    item['strength_compose'] = reader.ReadInt()
    item['vitality_compose'] = reader.ReadInt()
    item['intelligence_compose'] = reader.ReadInt()
    item['mind_compose'] = reader.ReadInt()
    item['agility_compose'] = reader.ReadInt()
    item['dexterity_compose'] = reader.ReadInt()
    item['lucky_compose'] = reader.ReadInt()
    item['hp_buildup'] = reader.ReadInt()
    item['strength_buildup'] = reader.ReadInt()
    item['vitality_buildup'] = reader.ReadInt()
    item['intelligence_buildup'] = reader.ReadInt()
    item['mind_buildup'] = reader.ReadInt()
    item['agility_buildup'] = reader.ReadInt()
    item['dexterity_buildup'] = reader.ReadInt()
    item['lucky_buildup'] = reader.ReadInt()
    item['buildup_limit'] = reader.ReadInt()
    item['default_weapon_proficiency_UnitProficiency'] = reader.ReadInt()
    item['default_shield_proficiency_UnitProficiency'] = reader.ReadInt()


def parse_unit_initial_parameters(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['hp_initial'] = reader.ReadInt()
    item['strength_initial'] = reader.ReadInt()
    item['vitality_initial'] = reader.ReadInt()
    item['intelligence_initial'] = reader.ReadInt()
    item['mind_initial'] = reader.ReadInt()
    item['agility_initial'] = reader.ReadInt()
    item['dexterity_initial'] = reader.ReadInt()
    item['lucky_initial'] = reader.ReadInt()
    item['level_max'] = reader.ReadInt()


def parse_unit_job(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['name'] = reader.ReadString(True)
    item['flavor'] = reader.ReadString(True)
    item['move_type_UnitMoveType'] = reader.ReadInt()
    item['movement'] = reader.ReadInt()
    item['hp_initial'] = reader.ReadInt()
    item['strength_initial'] = reader.ReadInt()
    item['vitality_initial'] = reader.ReadInt()
    item['intelligence_initial'] = reader.ReadInt()
    item['mind_initial'] = reader.ReadInt()
    item['agility_initial'] = reader.ReadInt()
    item['dexterity_initial'] = reader.ReadInt()
    item['lucky_initial'] = reader.ReadInt()
    item['job_rank_UnitJobRank'] = reader.ReadInt()
    item['job_characteristics_id'] = reader.ReadStringOrNull(True)
    item['spWeaponName1'] = reader.ReadString(True)
    item['spWeaponName2'] = reader.ReadString(True)
    item['classification_GearClassificationPattern'] = reader.ReadIntOrNull()
    item['new_cost'] = reader.ReadInt()
    item['variable_magic_bullet_name'] = reader.ReadString(True)
    item['rendering_pattern_UnitRenderingPattern'] = reader.ReadIntOrNull()


def parse_unit_type_parameter(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['unit_type_UnitType'] = reader.ReadInt()
    item['rarity_UnitRarity'] = reader.ReadInt()
    item['hp_levelup_max_correction'] = reader.ReadFloat()
    item['strength_levelup_max_correction'] = reader.ReadFloat()
    item['vitality_levelup_max_correction'] = reader.ReadFloat()
    item['intelligence_levelup_max_correction'] = reader.ReadFloat()
    item['mind_levelup_max_correction'] = reader.ReadFloat()
    item['agility_levelup_max_correction'] = reader.ReadFloat()
    item['dexterity_levelup_max_correction'] = reader.ReadFloat()
    item['lucky_levelup_max_correction'] = reader.ReadFloat()
    item['hp_compose_max'] = reader.ReadInt()
    item['strength_compose_max'] = reader.ReadInt()
    item['vitality_compose_max'] = reader.ReadInt()
    item['intelligence_compose_max'] = reader.ReadInt()
    item['mind_compose_max'] = reader.ReadInt()
    item['agility_compose_max'] = reader.ReadInt()
    item['dexterity_compose_max'] = reader.ReadInt()
    item['lucky_compose_max'] = reader.ReadInt()


def parse_unit_evolution_pattern(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['unit_UnitUnit'] = reader.ReadInt()
    item['target_unit_UnitUnit'] = reader.ReadInt()
    item['threshold_level'] = reader.ReadInt()
    item['money'] = reader.ReadInt()
