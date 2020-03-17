# -*- coding:utf-8 -*-
import datetime
import shutil
import time
from collections import defaultdict
from pathlib import Path
from typing import Optional

import click
import htmlmin
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

from potk_unit_extractor.loader import load_folder
from potk_unit_extractor.model import StatType, UnitType, UnitRarityStars, \
    ClassChangeType, UnitTagKind, Element, Skill, SkillType


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


def unit_sort_key(unit):
    return unit.any_name, unit.ID


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
    loader = load_folder(Path('cache'))
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

    if clean:
        shutil.rmtree(units_path, ignore_errors=True)
        shutil.rmtree(tags_path, ignore_errors=True)
        shutil.rmtree(skills_path, ignore_errors=True)
        shutil.rmtree(site_path / 'weapons', ignore_errors=True)
        shutil.rmtree(site_path / 'elements', ignore_errors=True)

    units_path.mkdir(exist_ok=True)
    tags_path.mkdir(exist_ok=True)
    skills_path.mkdir(exist_ok=True)

    stars = {
        # ★☆
        UnitRarityStars.ONE:   '★',
        UnitRarityStars.TWO:   '★★',
        UnitRarityStars.THREE: '★★★',
        UnitRarityStars.FOUR:  '★★★★',
        UnitRarityStars.FIVE:  '★★★★★',
        UnitRarityStars.SIX:   '★★★★★★',
    }

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

    if unit_ids:
        units = [loader.load_unit(int(u)) for u in unit_ids]
    else:
        units = list(loader.load_playable_units())

    print(f'Loaded {len(units)} units successfully')

    print(f'Computing groups...')
    units.sort(key=unit_sort_key)
    units_by_tag = group_units(units, key=lambda u: u.tags, iter_key=True)
    units_by_weapon = group_units(units, key=lambda u: u.gear_kind)
    units_by_element = group_units(units, key=lambda u: u.element)
    skill_icons = {s.ID: get_skill_icon_name(s)
                   for s in loader.skills_repo.all_skills}

    ovk_units = [unit for unit in units if unit.skills.ovk]
    ovk_units = group_units(ovk_units, key=lambda u: u.any_name)
    ovk_units = sorted((name, units) for name, units in ovk_units.items())

    template_shared_args = {
        'StatType':        StatType,
        'UnitType':        UnitType,
        'ClassChangeType': ClassChangeType,
        'stars':           stars,
        'jp_types':        jp_types,
        'jp_stats':        jp_stats,
        'cc_desc':         cc_desc,
        'badge_tag':       badge_tag,
        'badge_element':   badge_element,
        'tags':            sorted(units_by_tag.keys()),
        'weapons':         sorted(units_by_weapon.keys()),
        'elements':        sorted(units_by_element.keys()),
        'skill_icons':     skill_icons,
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
            unit=unit,
            **template_shared_args,
        )
        progress.inc()

    print(f'Rendering Skills lists to {skills_path}')
    ovk_path = skills_path / 'overkillers.html'
    render(
        template=env.get_template('ovk-skill-list.html'),
        out=ovk_path,
        minify=minify,
        unit_groups=ovk_units,
        **template_shared_args,
    )

    print(f'Rendering Tags to {tags_path}')
    tag_template = env.get_template('tag.html')
    progress = Progress(len(units_by_tag.items()))
    for tag, tag_units in units_by_tag.items():
        tag_units.sort(key=unit_sort_key)
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
            k_units.sort(key=unit_sort_key)
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
