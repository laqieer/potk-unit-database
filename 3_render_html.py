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

    units_by_tag = group_units(units, key=lambda u: u.tags)
    units_by_weapon = group_units(units, key=lambda u: u.gear_kind)
    units_by_element = group_units(units, key=lambda u: u.element)

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
    }

    open_args = {
        'mode':     'w',
        'encoding': 'utf-8',
        'newline':  '\n',
    }

    # Templates units pages
    for unit in units:
        output_path = units_path / f'{unit.ID}.html'
        print(output_path)
        with output_path.open(**open_args) as fp:
            env.get_template('unit.html').stream(
                unit=unit,
                **template_shared_args,
            ).dump(fp)

    # Templates units tags
    for tag, tag_units in units_by_tag.items():
        tag_units.sort(key=unit_sort_key)
        output_path = tags_path / f'{tag.uid}.html'
        print(output_path)
        with output_path.open(**open_args) as fp:
            env.get_template('tag.html').stream(
                tag=tag,
                units=tag_units,
                total=len(tag_units),
                **template_shared_args,
            ).dump(fp)

    generic_list_template = env.get_template('generic-unit-list.html')

    def render_generic_template(unit_map: dict, sub_path: str):
        generic_path = site_path / sub_path
        generic_path.mkdir(exist_ok=True)
        for k, k_units in unit_map.items():
            k_units.sort(key=unit_sort_key)
            out_path = generic_path / f'{k.value}.html'
            print(out_path)
            with out_path.open(**open_args) as fp:
                generic_list_template.stream(
                    page_title=k.name,
                    total=len(k_units),
                    units=k_units,
                    **template_shared_args,
                ).dump(fp)
        pass

    # Templates units weapons
    render_generic_template(units_by_weapon, 'weapons')
    # Templates units elements
    render_generic_template(units_by_element, 'elements')

    # Templates index page
    units.sort(key=unit_sort_key)
    index_path = site_path / 'index.html'
    print(index_path)
    with index_path.open(**open_args) as fp:
        env.get_template('index.html').stream(
            units=units,
            total=len(units),
            **template_shared_args,
        ).dump(fp)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
