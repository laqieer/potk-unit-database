# -*- coding: utf-8 -*-
import logging
from collections import defaultdict
from functools import lru_cache, cached_property
from typing import Optional, List, Tuple, Dict

from . import UnitMetadata
from ..master_data import MasterDataRepo, MasterData
from ..model import Skill, SkillType, SkillDesc, SkillGenre, SkillTarget, \
    Element, SkillEvo, UnitSkills, OvkSkill, SkillAwakeCategory

logger = logging.getLogger(__name__)


class SkillsRepo:
    def __init__(self, repo: MasterDataRepo):
        self._units: Dict[int, UnitMetadata] = {
            u.ID: u
            for u in map(UnitMetadata, repo.read(MasterData.UnitUnit))
        }

        self._skills = {
            skill.ID: skill
            for skill in (
                self._create_skill(s)
                for s in repo.read(MasterData.BattleskillSkill)
            )
        }

        self._evolutions = defaultdict(list)
        for evo in repo.read(MasterData.UnitSkillEvolution):
            evo = self._create_skill_evo(evo)
            self._evolutions[evo.unit_id].append(evo)

        self._ovk_skills = {
            ovk.same_character_id: ovk
            for ovk in (
                self._create_ovk_skill(d)
                for d in repo.read(MasterData.OverkillersSkillRelease)
            )
        }

        self._unit_skill = repo.group_by(
            key='unit_UnitUnit', res=MasterData.UnitSkill)
        self._unit_rs = repo.index(
            key='character_id', res=MasterData.UnitSkillAwake)
        self._unit_ls = repo.index(
            key='unit_UnitUnit', res=MasterData.UnitLeaderSkill)
        self._unit_cq = repo.group_by(
            key='unit_UnitUnit', res=MasterData.UnitSkillCharacterQuest)
        self._unit_hq = repo.index(
            key='character_UnitCharacter',
            res=MasterData.UnitSkillHarmonyQuest)
        self._unit_is = repo.index(
            key='unit_UnitUnit', res=MasterData.UnitSkillIntimate)

    @cached_property
    def all_skills(self) -> Tuple[Skill]:
        skills: List[Skill] = sorted(self._skills.values())
        return tuple(skills)

    def get_skill(self, skill_id: int) -> Skill:
        return self._skills[skill_id]

    @lru_cache(maxsize=None)
    def skills_of(self, unit_id: int) -> UnitSkills:
        unit = self._units[unit_id]
        evolutions = {s.from_skill: s for s in self._evolutions[unit.ID]}
        native = self._list_skills(unit_id, self._unit_skill)
        return UnitSkills(
            relationship=self._find_skill(unit.same_id, self._unit_rs),
            leader=self._find_skill(unit.ID, self._unit_ls),
            intimate=self._find_skill(unit.ID, self._unit_is),
            harmony=self._find_skill(unit.char_id, self._unit_hq),
            types={s.unit_type: s for s in native if s.unit_type},
            evolutions=evolutions,
            cq=tuple(sorted(self._list_skills(unit_id, self._unit_cq))),
            native=tuple(sorted(s for s in native if not s.unit_type)),
            ovk=self._ovk_skills.get(unit.same_id) if unit.has_ovk else None
        )

    def _list_skills(self, key: int, index: dict) -> List[Skill]:
        return [self._skills[link['skill_BattleskillSkill']]
                for link in index[key]]

    def _find_skill(self, key: int, index: dict) -> Optional[Skill]:
        if key not in index:
            return None
        skill_id = index[key]['skill_BattleskillSkill']
        return self._skills[skill_id]

    @staticmethod
    def _create_skill(skill: dict) -> Skill:
        category_id = skill['awake_skill_category_id']
        try:
            category = SkillAwakeCategory(category_id) if category_id > 1 else None
        except ValueError:
            logger.warning('ignored unmapped category for skill %d (category_id: %d)', skill['ID'], category_id)
            category = None
        return Skill(
            type=SkillType(skill['skill_type_BattleskillSkillType']),
            ID=skill['ID'],
            jp_desc=SkillDesc(
                name=skill['name'],
                full=skill['description'],
                short=skill['shortDescription'],
            ),
            en_desc=None,
            max_lv=skill['upper_level'],
            genres=tuple(sorted(
                SkillGenre(skill[k])
                for k in ['genre1_BattleskillGenre', 'genre2_BattleskillGenre']
                if skill[k]
            )),
            target=SkillTarget(skill['target_type_BattleskillTargetType']),
            element=Element(skill['element_CommonElement']),
            category=category,
            use_count=skill['use_count'],
            cooldown_turns=skill['charge_turn'],
            max_use_per_quest=skill['max_use_count'],
            min_range=skill['min_range'],
            max_range=skill['max_range'],
            weight=skill['weight'],
            power=skill['power'],
            hp_cost=skill['consume_hp'],
            resource_id=skill['resource_reference_id'],
        )

    def _create_skill_evo(self, evo: dict) -> SkillEvo:
        return SkillEvo(
            unit_id=evo['unit_UnitUnit'],
            from_skill=self._skills[evo['before_skill_BattleskillSkill']],
            to_skill=self._skills[evo['after_skill_BattleskillSkill']],
            req_level=evo['level'],
        )

    def _create_ovk_skill(self, ovk: dict) -> OvkSkill:
        return OvkSkill(
            same_character_id=ovk['ID'],
            skill=self._skills[ovk['skill_BattleskillSkill']],
            req_dv=ovk['unity_value'],
        )
