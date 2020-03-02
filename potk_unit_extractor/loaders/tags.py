# -*- coding: utf-8 -*-
from functools import lru_cache
from typing import Dict, Tuple

from ..master_data import MasterDataRepo, MasterData
from ..model import UnitTag, UnitTagKind, UnitTagDesc
from ..translations import TAGS

GROUP_FIELD_TAG_KIND = {
    "group_large_category_id_UnitGroupLargeCategory":
        UnitTagKind.LARGE,
    "group_small_category_id_UnitGroupSmallCategory":
        UnitTagKind.SMALL,
    "group_clothing_category_id_UnitGroupClothingCategory":
        UnitTagKind.CLOTHING,
    "group_clothing_category_id_2_UnitGroupClothingCategory":
        UnitTagKind.CLOTHING,
    "group_generation_category_id_UnitGroupGenerationCategory":
        UnitTagKind.GENERATION,
}

GROUP_RES_TAG_KIND = {
    UnitTagKind.LARGE:      MasterData.UnitGroupLargeCategory,
    UnitTagKind.SMALL:      MasterData.UnitGroupSmallCategory,
    UnitTagKind.CLOTHING:   MasterData.UnitGroupClothingCategory,
    UnitTagKind.GENERATION: MasterData.UnitGroupGenerationCategory,
}


class TagRepo:
    def __init__(self, repo: MasterDataRepo):
        self._repo = repo
        self._unit_groups = repo.index(key='unit_id', res=MasterData.UnitGroup)
        self._tags: Dict[UnitTagKind, Dict[int, UnitTag]] = {
            k: self._create_tags(k) for k in UnitTagKind
        }

    @lru_cache(maxsize=None)
    def tags_of(self, unit_id: int) -> Tuple[UnitTag]:
        group = self._unit_groups.get(unit_id)
        if not group:
            return tuple()
        return tuple(sorted(
            self._tags[kind][group[field]]
            for field, kind in GROUP_FIELD_TAG_KIND.items()
        ))

    def _create_tags(self, kind: UnitTagKind) -> Dict[int, UnitTag]:
        res = GROUP_RES_TAG_KIND[kind]
        return {
            tag.ID: tag
            for tag in (
                self._create_tag(kind, d) for d in self._repo.read(res)
            )
        }

    @staticmethod
    def _create_tag(kind: UnitTagKind, data: dict) -> UnitTag:
        tag_id = data['ID']
        translation_key = (kind, tag_id)
        return UnitTag(
            ID=tag_id,
            kind=kind,
            desc_jp=UnitTagDesc(
                name=data['name'],
                short_label_name=data['short_label_name'],
                description=data['description'],
            ),
            desc_en=TAGS.get(translation_key)
        )
