from pathlib import Path
from typing import Tuple

from .loaders.class_changes import CCRepo
from .loaders.jobs import JobsRepo
from .loaders.skills import SkillsRepo
from .loaders.stats import StatsRepo
from .loaders.tags import TagRepo
from .master_data import MasterDataRepo, MasterData
from .model import Element, UnitData, UnitRarityStars, GearKind, Skill

# From game. Yes, it's hardcoded there too.

ELEMENTAL_SKILLS_IDS = [
    490000010, 490000013, 490000015, 490000017, 490000019, 490000021, 490000173
]


class Loader:
    """OOP Based loader for unit data based on raw lists-of-dicts.
    """

    def __init__(self, repo: MasterDataRepo):
        self.tag_repo = TagRepo(repo)
        self.skills_repo = SkillsRepo(repo)
        self.job_repo = JobsRepo(repo)
        self.cc_repo = CCRepo(repo, self.job_repo)
        self.stats_repo = StatsRepo(repo, self.job_repo)
        self.units = repo.index(
            key='ID', res=MasterData.UnitUnit)

    def load_playable_units(self):
        """
        Loads all units with IsNormalUnit=True (game code).

        :return: Generator of all loaded units, in no particular order.
        """
        excludes = [
            range(700000, 999999),  # .     700k, OG Misc
            range(1000000, 1999999),  # .     1m, Earth Males
            range(2700000, 2999999),  # .     2m, PoL Misc
            range(3700000, 3999999),  # .     3m, LR Misc
            range(4700000, 4999999),  # .     4m, Extra Art Misc
            range(5700000, 5999999),  # .     5m, IN Misc
            range(7000000, 7999999),  # .     7m, Taga Enemies?
            range(10000000, 19999999),  # .  10m, Laev Enemies?
            range(30000000, 39999999),  # .  30m, Guild Structures
            range(70000000, 79999999),  # .  70m, Memories, Cards, etc
            range(80000000, 89999999),  # .  80m, Innocents
            range(700000000, 799999999),  # 700m, Male Memories
            range(800000000, 899999999),  # 800m, Male Innocents
        ]
        generator = (
            unit['ID'] for unit in self.units.values()
            if not any(unit['ID'] in r for r in excludes)
        )
        for unit_id in generator:
            unit = self.load_unit(unit_id)
            # Some weird tyr versions are mixed in the fatom range.
            if unit.element != Element.NONE:
                yield unit

    def load_unit(self, unit_id: int) -> UnitData:
        unit = self.units[unit_id]
        same_ch_id = unit['same_character_id']
        has_ovk = unit['exist_overkillers_skill']
        skills = self.skills_repo.skills_of(unit_id, same_ch_id, has_ovk)

        return UnitData(
            ID=unit_id,
            same_character_id=same_ch_id,
            character_id=unit['character_UnitCharacter'],
            resource_id=unit['resource_reference_unit_id_UnitUnit'],
            jp_name=unit['name'],
            eng_name=unit['english_name'],
            element=_compute_element(skills.basic),
            gear_kind=GearKind(unit['kind_GearKind']),
            level=self.stats_repo.load_level(unit_id),
            rarity=UnitRarityStars(unit['rarity_UnitRarity']),
            job=self.job_repo.get_job(unit['job_UnitJob']),
            cost=unit['cost'],
            is_awakened=(1 == unit['awake_unit_flag']),
            stats=self.stats_repo.load_stats(unit_id),
            cc=self.cc_repo.unit_cc(unit_id),
            tags=self.tag_repo.tags_of(unit_id),
            skills=skills,
        )


def _compute_element(skills: Tuple[Skill]) -> Element:
    for skill in skills:
        if skill.ID in ELEMENTAL_SKILLS_IDS:
            return skill.element
    return Element.NONE


def load_folder(path: Path) -> Loader:
    """
    Loads unit data from a folder containing json files in a predefined
    structure.

    :param path: Path of the folder containing the files.
    :return: Populated loader.
    """
    return Loader(MasterDataRepo(path))
