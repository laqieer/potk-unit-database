from .master_data_reader import MasterDataReader


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
    item['unit_voice_pattern_id'] = reader.ReadInt()
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
    item['is_unity_value_up'] = reader.ReadBool()
    item['job_characteristics_levelup_pattern'] = reader.ReadBool()
    item['exist_overkillers_slot'] = reader.ReadBool()
    item['exist_overkillers_skill'] = reader.ReadBool()
    item['overkillers_parameter'] = reader.ReadInt()
    item['expire_date_UnitExpireDate'] = reader.ReadIntOrNull()


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


def parse_unit_compose_setting(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['hp_compose_add_max'] = reader.ReadStringOrNull(True)
    item['strength_compose_add_max'] = reader.ReadStringOrNull(True)
    item['vitality_compose_add_max'] = reader.ReadStringOrNull(True)
    item['intelligence_compose_add_max'] = reader.ReadStringOrNull(True)
    item['mind_compose_add_max'] = reader.ReadStringOrNull(True)
    item['agility_compose_add_max'] = reader.ReadStringOrNull(True)
    item['dexterity_compose_add_max'] = reader.ReadStringOrNull(True)
    item['lucky_compose_add_max'] = reader.ReadStringOrNull(True)
    item['name'] = reader.ReadString(True)
    item['description'] = reader.ReadString(True)


def parse_unit_rarity(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['name'] = reader.ReadString(True)
    item['index'] = reader.ReadInt()
    item['sell_rarity_medal'] = reader.ReadInt()
    item['skill_levelup_rate'] = reader.ReadInt()
    item['indicator_level_rate'] = reader.ReadFloat()
    item['reincarnation_level'] = reader.ReadInt()
    item['trust_rate'] = reader.ReadFloat()


def parse_gear_kind(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['name'] = reader.ReadString(True)
    item['can_equip'] = reader.ReadInt()
    item['same_element'] = reader.ReadInt()
    item['is_attack'] = reader.ReadBool()
    item['is_composite'] = reader.ReadBool()
    item['colosseum_preempt_coefficient'] = reader.ReadInt()


def parse_job_change_pattern(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['unit_UnitUnit'] = reader.ReadInt()
    item['job_UnitJob'] = reader.ReadInt()
    item['job1_UnitJob'] = reader.ReadInt()
    item['materials1_JobChangeMaterials'] = reader.ReadIntOrNull()
    item['job2_UnitJob'] = reader.ReadInt()
    item['materials2_JobChangeMaterials'] = reader.ReadInt()
    item['job3_UnitJob'] = reader.ReadIntOrNull()
    item['materials3_JobChangeMaterials'] = reader.ReadIntOrNull()
    item['job4_UnitJob'] = reader.ReadIntOrNull()
    item['materials4_JobChangeMaterials'] = reader.ReadIntOrNull()


def parse_job_characteristics(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['skill_BattleskillSkill'] = reader.ReadInt()
    item['skill2_BattleskillSkill'] = reader.ReadIntOrNull()
    item['level_pattern_id'] = reader.ReadStringOrNull(True)
    item['levelmax_bonus_JobCharacteristicsLevelmaxBonus'] = reader.ReadInt()
    item['levelmax_bonus_value'] = reader.ReadInt()


def parse_unit_skill(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['unit_UnitUnit'] = reader.ReadInt()
    item['level'] = reader.ReadInt()
    item['skill_BattleskillSkill'] = reader.ReadInt()
    item['unit_type'] = reader.ReadInt()


def parse_unit_cq(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['unit_UnitUnit'] = reader.ReadInt()
    item['character_quest_QuestCharacterS'] = reader.ReadInt()
    item['skill_BattleskillSkill'] = reader.ReadInt()
    item['quest_id_for_evolution'] = reader.ReadInt()
    item['skill_after_evolution'] = reader.ReadInt()


def parse_unit_hq(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['character_UnitCharacter'] = reader.ReadInt()
    item['character_quest_QuestHarmonyS'] = reader.ReadInt()
    item['skill_BattleskillSkill'] = reader.ReadInt()


def parse_unit_skill_link(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['unit_UnitUnit'] = reader.ReadInt()
    item['skill_BattleskillSkill'] = reader.ReadInt()


def parse_unit_skill_evo(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['unit_UnitUnit'] = reader.ReadInt()
    item['before_skill_BattleskillSkill'] = reader.ReadInt()
    item['level'] = reader.ReadInt()
    item['after_skill_BattleskillSkill'] = reader.ReadInt()


def parse_unit_rs(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['character_id'] = reader.ReadInt()
    item['need_affection'] = reader.ReadFloat()
    item['skill_BattleskillSkill'] = reader.ReadInt()


def parse_battle_skill(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['name'] = reader.ReadString(True)
    item['description'] = reader.ReadString(True)
    item['shortDescription'] = reader.ReadString(True)
    item['shortDescriptionEnemy'] = reader.ReadString(True)
    item['skill_type_BattleskillSkillType'] = reader.ReadInt()
    item['element_CommonElement'] = reader.ReadInt()
    item['genre1_BattleskillGenre'] = reader.ReadIntOrNull()
    item['genre2_BattleskillGenre'] = reader.ReadIntOrNull()
    item['target_type_BattleskillTargetType'] = reader.ReadInt()
    item['min_range'] = reader.ReadInt()
    item['max_range'] = reader.ReadInt()
    item['consume_hp'] = reader.ReadInt()
    item['weight'] = reader.ReadInt()
    item['power'] = reader.ReadInt()
    item['use_count'] = reader.ReadInt()
    item['charge_turn'] = reader.ReadInt()
    item['duel_magic_bullet_name'] = reader.ReadString(True)
    item['variable_magic_bullet_flag'] = reader.ReadBool()
    item['field_effect_name'] = reader.ReadString(True)
    item['field_target_effect_name'] = reader.ReadString(True)
    item['upper_level'] = reader.ReadInt()
    item['field_effect_BattleskillFieldEffect'] = reader.ReadIntOrNull()
    item['duel_effect_BattleskillDuelEffect'] = reader.ReadIntOrNull()
    item['passive_effect_BattleskillFieldEffect'] = reader.ReadIntOrNull()
    item['time_of_death_skill_disable'] = reader.ReadBool()
    item['ailment_effect_BattleskillAilmentEffect'] = reader.ReadIntOrNull()
    item['range_effect_passive_skill'] = reader.ReadBool()
    item['max_use_count'] = reader.ReadInt()
    item['awake_skill_category_id'] = reader.ReadInt()
    item['resource_reference_id'] = reader.ReadInt()


def parse_unit_group(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['unit_id'] = reader.ReadInt()
    item['group_large_category_id_UnitGroupLargeCategory'] = reader.ReadInt()
    item['group_small_category_id_UnitGroupSmallCategory'] = reader.ReadInt()
    item['group_clothing_category_id_UnitGroupClothingCategory'] \
        = reader.ReadInt()
    item['group_clothing_category_id_2_UnitGroupClothingCategory'] \
        = reader.ReadInt()
    item['group_generation_category_id_UnitGroupGenerationCategory'] \
        = reader.ReadInt()


def parse_unit_group_category(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['name'] = reader.ReadString(True)
    item['short_label_name'] = reader.ReadString(True)
    item['description'] = reader.ReadString(True)
    item['start_at'] = reader.ReadDateTimeOrNull()


def parse_ovk_skill_release(reader: MasterDataReader, item: dict):
    item['ID'] = reader.ReadInt()
    item['unity_value'] = reader.ReadInt()
    item['skill_BattleskillSkill'] = reader.ReadInt()
