# -*- coding:utf-8 -*-
from jinja2 import Environment, FileSystemLoader, select_autoescape
from potk_unit_extractor.model import StatType, UnitType, UnitRarityStars
from potk_unit_extractor.loader import load_folder
from pathlib import Path


def main(unit_ids: list):
    loader = load_folder(Path('masterdata'))
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html']),
    )
    template = env.get_template('unit.html')

    stars = {
        UnitRarityStars.ONE:   '☆',
        UnitRarityStars.TWO:   '☆☆',
        UnitRarityStars.THREE: '☆☆☆',
        UnitRarityStars.FOUR:  '☆☆☆☆',
        UnitRarityStars.FIVE:  '☆☆☆☆☆',
        UnitRarityStars.SIX:   '☆☆☆☆☆☆',
    }

    for unit_id in unit_ids:
        unit = loader.load_unit(int(unit_id))
        template.stream(
            unit=unit,
            StatType=StatType,
            UnitType=UnitType,
            stars=stars,
        ).dump(f'site/{unit.eng_name.lower()}-{unit_id}.html')


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
