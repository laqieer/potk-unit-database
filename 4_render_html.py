# -*- coding:utf-8 -*-
from jinja2 import Environment, FileSystemLoader, select_autoescape
from potk_unit_extractor.model import StatType, UnitType, UnitRarityStars, \
    ClassChangeType
from potk_unit_extractor.loader import load_folder
from pathlib import Path


def main(unit_ids: list):
    loader = load_folder(Path('masterdata'))
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html']),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    unit_template = env.get_template('unit.html')

    site_path = Path('site')
    units_path = site_path / 'units'
    units_path.mkdir(exist_ok=True)

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

    cc_desc = {
        ClassChangeType.NORMAL: '6★',
        ClassChangeType.VERTEX1: 'VERTEX 1',
        ClassChangeType.VERTEX2: 'VERTEX 2',
        ClassChangeType.VERTEX3: 'VERTEX 3',
    }

    if unit_ids:
        generator = (loader.load_unit(int(u)) for u in unit_ids)
    else:
        generator = loader.load_playable_units()

    units = []
    for unit in generator:
        units.append(unit)
        output_path = units_path / f'{unit.ID}.html'
        print(output_path)
        with output_path.open(mode='w', encoding='utf8') as fp:
            unit_template.stream(
                unit=unit,
                StatType=StatType,
                UnitType=UnitType,
                ClassChangeType=ClassChangeType,
                stars=stars,
                jp_types=jp_types,
                cc_desc=cc_desc,
            ).dump(fp)

    units.sort(key=lambda u: (u.any_name, u.ID))
    index_path = site_path / 'index.html'
    print(index_path)
    with index_path.open(mode='w', encoding='utf8') as fp:
        env.get_template('index.html').stream(
            units=units,
            total=len(units),
            stars=stars,
        ).dump(fp)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
