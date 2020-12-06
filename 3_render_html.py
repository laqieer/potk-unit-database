# -*- coding:utf-8 -*-
import datetime
import heapq
import shutil
import time
from collections import defaultdict
from operator import attrgetter
from pathlib import Path
from typing import Optional, List, Tuple, Iterable

import click
import htmlmin
import js2py  # To pre-compute the FlexSearch index.
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

from potk_unit_extractor.loader import load_folder
from potk_unit_extractor.model import StatType, UnitType, ClassChangeType, UnitTagKind, Element, Skill, SkillType, \
    SkillAwakeCategory, UnitData


class Progress:
    def __init__(self, total: int):
        self.total = total
        self.curr = 0
        self.last = time.time()

    def inc(self):
        self.curr += 1
        now = time.time()
        if now - self.last > 5:
            print(f'  {self.curr}/{self.total}')
            self.last = now


def sort_units(units: list):
    # Python sorting preserves original order.
    # Python sorting also is efficient on consecutive sorting.
    units.sort(key=attrgetter('ID'), reverse=True)
    units.sort(key=attrgetter('tags', 'any_name'))
    units.sort(key=attrgetter('published_at'), reverse=True)
    return units


def group_units(units: list, key: callable, iter_key: bool = False) -> dict:
    result = defaultdict(list)
    for unit in units:
        key_val = key(unit)
        if iter_key:
            for item in key_val:
                result[item].append(unit)
        else:
            result[key_val].append(unit)
    return result


def expand_unit(unit: UnitData) -> List[UnitData]:
    result: List[UnitData] = [unit]
    while unit.evolved_from:
        result.append(unit.evolved_from)
        unit = unit.evolved_from
    return list(reversed(result))


def compute_latest_releases(sorted_units: List[UnitData]) -> Iterable[Tuple]:
    releases = group_units(sorted_units, key=attrgetter('published_at'))
    last_3 = heapq.nlargest(3, releases.keys())
    return zip(last_3, (releases[k] for k in last_3))


def get_skill_icon_name(skill: Skill) -> Optional[str]:
    # CC Skills (ability) are handled on the template.
    if skill.type == SkillType.LEADER:
        return 'leader'
    elif skill.type == SkillType.ITEM:
        return 'supply'
    elif skill.type == SkillType.MAGIC:
        # TODO Use bullet icons
        return None
    else:
        rid = skill.resource_id or skill.ID
        return f'{rid}'


def render(template: Template, out: Path, minify: bool, **render_args):
    html = template.render(**render_args)
    if minify:
        html = htmlmin.minify(html)
    with out.open(mode='w', encoding='utf-8', newline='\n') as fp:
        fp.write(html)


@click.command()
@click.option('--minify', is_flag=True, default=False)
@click.option('--clean', is_flag=True, default=False)
@click.argument('unit_ids', nargs=-1)
def main(minify: bool, clean: bool, unit_ids: list):
    exec_start = datetime.datetime.now()
    print('Loading Units...')
    loader = load_folder(Path('cache', 'current'))
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html']),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    site_path = Path('site')
    site_path.mkdir(exist_ok=True)

    units_path = site_path / 'units'
    tags_path = site_path / 'tags'
    skills_path = site_path / 'skills'
    flex_search_path = site_path / 'search'

    if clean:
        shutil.rmtree(units_path, ignore_errors=True)
        shutil.rmtree(tags_path, ignore_errors=True)
        shutil.rmtree(skills_path, ignore_errors=True)
        shutil.rmtree(flex_search_path, ignore_errors=True)
        shutil.rmtree(site_path / 'weapons', ignore_errors=True)
        shutil.rmtree(site_path / 'elements', ignore_errors=True)

    units_path.mkdir(exist_ok=True)
    tags_path.mkdir(exist_ok=True)
    skills_path.mkdir(exist_ok=True)
    flex_search_path.mkdir(exist_ok=True)

    def stars(unit: UnitData, final: UnitData) -> str:
        """★☆"""
        blank = final.rarity.stars_count - unit.rarity.stars_count
        return '★' * unit.rarity.stars_count + '☆' * blank

    # TODO Remove and use t.jp_ch directly
    jp_types = {t: t.jp_ch for t in UnitType}

    jp_stats = {
        StatType.HP:  '',
        StatType.STR: '力',
        StatType.MGC: '魔',
        StatType.GRD: '守',
        StatType.SPR: '精',
        StatType.SPD: '速',
        StatType.TEC: '技',
        StatType.LCK: '運',
    }

    cc_desc = {
        ClassChangeType.NORMAL:  '6★',
        ClassChangeType.VERTEX1: 'Vertex 1',
        ClassChangeType.VERTEX2: 'Vertex 2',
        ClassChangeType.VERTEX3: 'Vertex 3',
    }

    badge_tag = {
        UnitTagKind.LARGE:      'badge-danger',
        UnitTagKind.SMALL:      'badge-warning',
        UnitTagKind.CLOTHING:   'badge-primary',
        UnitTagKind.GENERATION: 'badge-dark',
        UnitTagKind.CUSTOM:     'badge-success',
    }

    badge_element = {
        Element.NONE:    'badge-secondary',
        Element.FIRE:    'badge-danger',
        Element.ICE:     'badge-primary',
        Element.WIND:    'badge-success',
        Element.THUNDER: 'badge-warning',
        Element.LIGHT:   'badge-light',
        Element.DARK:    'badge-dark',
    }

    category_desc = {
        SkillAwakeCategory.TRUST:         'Trust',
        SkillAwakeCategory.GENERIC_RS:    'Global RS',
        SkillAwakeCategory.CHAOS_RS:      'Chaos RS',
        SkillAwakeCategory.HARMONIA_RS:   'Harmonia RS',
        SkillAwakeCategory.TREISEMA_RS:   'Treisema RS',
        SkillAwakeCategory.TYRHELM_RS:    'Tyrhelm RS',
        SkillAwakeCategory.COMMAND_RS:    'Command Gear',
        SkillAwakeCategory.INTEGRAL_GEAR: 'Integral Gear',
        SkillAwakeCategory.SCHOOL_GEAR:   'School Gear',
        SkillAwakeCategory.IMITATE_GEAR:  'Imitate Gear',
    }

    category_comment = {
        SkillAwakeCategory.TRUST:
            ("Trust Skills are obtained from PoL Units. "
             "They're not faction locked, and can only be used by PoL Units."),
        SkillAwakeCategory.GENERIC_RS:
            ("Global Resonance Skills available to every unit that has an "
             "RS Slot. Cannot be used by pure PoL Units, but can be used by "
             "LR PoL units."),
        SkillAwakeCategory.CHAOS_RS:
            ("Resonance Skills obtained from Lost Ragnarok units of the "
             "Chaos Lion Empire faction. "
             "Can only be use by Special units and Chaos Lion units."),
        SkillAwakeCategory.HARMONIA_RS:
            ("Resonance Skills obtained from Lost Ragnarok units of the "
             "Harmonia Pontificate faction. "
             "Can only be use by Special units and Harmonia units."),
        SkillAwakeCategory.TREISEMA_RS:
            ("Resonance Skills obtained from Lost Ragnarok units of the "
             "Treisema Republic faction. "
             "Can only be use by Special units and Treisema units."),
        SkillAwakeCategory.TYRHELM_RS:
            ("Resonance Skills obtained from Lost Ragnarok units of the "
             "Tyrhelm faction. "
             "Can only be use by Special units and Tyrhelm units."),
        SkillAwakeCategory.COMMAND_RS:
            ("Resonance Skills obtained from Command Killers. "
             "Can only be use by Special units and Command Killers."),
        SkillAwakeCategory.INTEGRAL_GEAR:
            ("Gear Skills obtained from Integral Killers. "
             "Can only be use by Special units and Integral Killers."),
        SkillAwakeCategory.SCHOOL_GEAR:
            ("Gear Skills obtained from School Units. "
             "Can only be use by School Units."),
        SkillAwakeCategory.IMITATE_GEAR:
            ("Gear Skills obtained from Imitate Killers. "
             "Can only be use by Special units and Imitate Killers."),
    }

    if unit_ids:
        units = [loader.load_unit(int(u)) for u in unit_ids]
    else:
        units = [u for u in loader.load_playable_units() if not u.can_evolve]

    print(f'Loaded {len(units)} units successfully')

    print(f'Computing groups...')
    sort_units(units)
    units_by_tag = group_units(units, key=lambda u: u.tags, iter_key=True)
    units_by_weapon = group_units(units, key=lambda u: u.gear_kind)
    units_by_element = group_units(units, key=lambda u: u.element)
    latest_releases = compute_latest_releases(units)
    skill_icons = {s.ID: get_skill_icon_name(s)
                   for s in loader.skills_repo.all_skills}

    ovk_units = [unit for unit in units if unit.skills.ovk]
    ovk_units = group_units(ovk_units, key=lambda u: u.any_name)
    ovk_units = sorted((name, units) for name, units in ovk_units.items())

    rs_units = {
        c: sorted(
            (u for u in units
             if u.skills.relationship
             if u.skills.relationship.category == c),
            key=attrgetter('any_name', 'ID')
        )
        for c in SkillAwakeCategory
    }

    print(f'Computing search index...')
    with open('./js/flexsearch-0.6.22.min.js', mode='r', encoding='utf-8') as fd:
        flex_js_code = fd.read()
    flex_search = js2py.eval_js(flex_js_code + '; FlexSearch')
    search_index = flex_search.create()
    for unit in units:
        search_index.add(unit.ID, unit.h_id)
    with (flex_search_path / 'units.index.txt').open(mode='w', encoding='utf-8') as fd:
        fd.write(search_index.export())

    template_shared_args = {
        'StatType':           StatType,
        'UnitType':           UnitType,
        'ClassChangeType':    ClassChangeType,
        'SkillAwakeCategory': SkillAwakeCategory,
        'stars':              stars,
        'jp_types':           jp_types,
        'jp_stats':           jp_stats,
        'cc_desc':            cc_desc,
        'category_desc':      category_desc,
        'category_comment':   category_comment,
        'badge_tag':          badge_tag,
        'badge_element':      badge_element,
        'tags':               sorted(units_by_tag.keys()),
        'weapons':            sorted(units_by_weapon.keys()),
        'elements':           sorted(units_by_element.keys()),
        'skill_icons':        skill_icons,
    }

    print(f'Rendering Units to {units_path}')
    progress = Progress(len(units))
    unit_template = env.get_template('unit.html')
    for unit in units:
        output_path = units_path / f'{unit.ID}.html'
        render(
            template=unit_template,
            out=output_path,
            minify=minify,
            final_unit=unit,
            units=expand_unit(unit),
            **template_shared_args,
        )
        progress.inc()

    print(f'Rendering Skills lists to {skills_path}')
    progress = Progress(len(rs_units.keys()) + 1)
    ovk_path = skills_path / 'overkillers.html'
    render(
        template=env.get_template('ovk-skill-list.html'),
        out=ovk_path,
        minify=minify,
        cd_root='..',
        unit_groups=ovk_units,
        **template_shared_args,
    )
    progress.inc()
    generic_rs_list_template = env.get_template('rs-skill-list.html')
    for category, cat_units in rs_units.items():
        cat_path = skills_path / f'{category.name.lower()}.html'
        render(
            template=generic_rs_list_template,
            out=cat_path,
            minify=minify,
            cd_root='..',
            category=category,
            units=cat_units,
            **template_shared_args,
        )
        progress.inc()

    print(f'Rendering Tags to {tags_path}')
    tag_template = env.get_template('tag.html')
    progress = Progress(len(units_by_tag.items()))
    for tag, tag_units in units_by_tag.items():
        sort_units(tag_units)
        output_path = tags_path / f'{tag.uid}.html'
        render(
            template=tag_template,
            out=output_path,
            minify=minify,
            tag=tag,
            units=tag_units,
            total=len(tag_units),
            **template_shared_args,
        )
        progress.inc()

    generic_list_template = env.get_template('generic-unit-list.html')

    def render_generic_template(unit_map: dict, sub_path: str):
        generic_path = site_path / sub_path
        generic_path.mkdir(exist_ok=True)
        print(f'Rendering {sub_path.title()} to {generic_path}')
        progress = Progress(len(unit_map.items()))
        for k, k_units in unit_map.items():
            sort_units(k_units)
            out_path = generic_path / f'{k.value}.html'
            render(
                template=generic_list_template,
                out=out_path,
                minify=minify,
                page_title=k.name,
                total=len(k_units),
                units=k_units,
                **template_shared_args,
            )
            progress.inc()

    render_generic_template(units_by_weapon, 'weapons')
    render_generic_template(units_by_element, 'elements')

    index_path = site_path / 'index.html'
    print(f'Rendering {index_path}')
    render(
        template=env.get_template('index.html'),
        out=index_path,
        minify=minify,
        units=units,
        latest_releases=latest_releases,
        total=len(units),
        **template_shared_args,
    )

    elapsed_time = datetime.datetime.now() - exec_start
    count_ovk = sum(len(units) for _, units in ovk_units)
    print(f'\nAll pages rendered successfully in {elapsed_time}')
    print(f'{len(units)} Units')
    print(f'{len(units_by_tag.keys())} Tags')
    print(f'{count_ovk} Overkiller Skills')


if __name__ == '__main__':
    main()
