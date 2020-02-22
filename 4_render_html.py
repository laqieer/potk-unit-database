# -*- coding:utf-8 -*-
from jinja2 import Environment, FileSystemLoader, select_autoescape
from potk_unit_extractor.model import StatType, UnitType, UnitRarityStars, \
    ClassChangeType, UnitTagKind, Element
from potk_unit_extractor.loader import load_folder
from pathlib import Path


def unit_sort_key(unit):
    return unit.any_name, unit.ID


def group_units(units: list, key: callable) -> dict:
    result = {}

    def add(k, v):
        if k in result:
            result[k].append(v)
        else:
            result[k] = [v]

    for unit in units:
        key_val = key(unit)
        try:
            iterator = iter(key_val)
        except TypeError:
            add(key_val, unit)
        else:
            for item in iterator:
                add(item, unit)

    return result


def main(unit_ids: list):
    loader = load_folder(Path('masterdata'))
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html']),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    site_path = Path('site')
    units_path = site_path / 'units'
    units_path.mkdir(exist_ok=True)
    tags_path = site_path / 'tags'
    tags_path.mkdir(exist_ok=True)
    weapons_path = site_path / 'weapons'
    weapons_path.mkdir(exist_ok=True)

    stars = {
        # ★☆
        UnitRarityStars.ONE:   '★',
        UnitRarityStars.TWO:   '★★',
        UnitRarityStars.THREE: '★★★',
        UnitRarityStars.FOUR:  '★★★★',
        UnitRarityStars.FIVE:  '★★★★★',
        UnitRarityStars.SIX:   '★★★★★★',
    }

    jp_types = {
        UnitType.BAL: '王',
        UnitType.VIT: '命',
        UnitType.STR: '攻',
        UnitType.MGC: '魔',
        UnitType.GRD: '守',
        UnitType.DEX: '匠',
    }

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
        Element.FIRE:    'badge-danger',
        Element.ICE:     'badge-primary',
        Element.WIND:    'badge-success',
        Element.THUNDER: 'badge-warning',
        Element.LIGHT:   'badge-light',
        Element.DARK:    'badge-dark',
    }

    if unit_ids:
        generator = (loader.load_unit(int(u)) for u in unit_ids)
    else:
        generator = loader.load_playable_units()

    # Templates units pages
    units = []
    for unit in generator:
        units.append(unit)
        output_path = units_path / f'{unit.ID}.html'
        print(output_path)
        with output_path.open(mode='w', encoding='utf8') as fp:
            env.get_template('unit.html').stream(
                unit=unit,
                StatType=StatType,
                UnitType=UnitType,
                ClassChangeType=ClassChangeType,
                stars=stars,
                jp_types=jp_types,
                jp_stats=jp_stats,
                cc_desc=cc_desc,
                badge_tag=badge_tag,
            ).dump(fp)

    # Templates units tags
    units_by_tag = group_units(units, key=lambda u: u.tags)
    for tag, tag_units in units_by_tag.items():
        tag_units.sort(key=unit_sort_key)
        output_path = tags_path / f'{tag.uid}.html'
        print(output_path)
        with output_path.open(mode='w', encoding='utf8') as fp:
            env.get_template('tag.html').stream(
                tag=tag,
                units=tag_units,
                stars=stars,
                badge_tag=badge_tag,
            ).dump(fp)

    generic_list_template = env.get_template('generic-unit-list.html')

    def render_generic_template(unit_map: dict, sub_path: str):
        generic_path = site_path / sub_path
        generic_path.mkdir(exist_ok=True)
        for k, k_units in unit_map.items():
            k_units.sort(key=unit_sort_key)
            out_path = generic_path / f'{k.value}.html'
            print(out_path)
            with out_path.open(mode='w', encoding='utf8') as fp:
                generic_list_template.stream(
                    page_title=k.name,
                    total=len(k_units),
                    units=k_units,
                    stars=stars,
                    badge_tag=badge_tag,
                ).dump(fp)
        pass

    # Templates units weapons
    units_by_weapon = group_units(units, key=lambda u: u.gear_kind)
    render_generic_template(units_by_weapon, 'weapons')
    # Templates units elements
    units_by_element = group_units(units, key=lambda u: u.element)
    render_generic_template(units_by_element, 'elements')

    # Templates index page
    units.sort(key=unit_sort_key)
    index_path = site_path / 'index.html'
    print(index_path)
    with index_path.open(mode='w', encoding='utf8') as fp:
        env.get_template('index.html').stream(
            units=units,
            total=len(units),
            tags=sorted(units_by_tag.keys()),
            weapons=sorted(units_by_weapon.keys()),
            elements=sorted(units_by_element.keys()),
            stars=stars,
            badge_tag=badge_tag,
            badge_element=badge_element,
        ).dump(fp)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
