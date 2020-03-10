# -*- coding: utf-8 -*-


class UnitMetadata:
    def __init__(self, unit_dict: dict):
        self.ID: int = unit_dict['ID']
        self.same_id: int = unit_dict['same_character_id']
        self.char_id: int = unit_dict['character_UnitCharacter']
        self.job_id: int = unit_dict['job_UnitJob']
        self.rarity: int = unit_dict['rarity_UnitRarity']
        self.is_awake: bool = 1 == unit_dict['awake_unit_flag']
        self.has_ovk: bool = unit_dict['exist_overkillers_skill']
        self.ud_id: int = unit_dict[
            'compose_max_unity_value_setting_id_ComposeMaxUnityValueSetting']
