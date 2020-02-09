# -*- coding:utf-8 -*-
from potk_unit_extractor.loader import Loader
import json


def main(unit_ids: list):
    loader = Loader(
        units=load('masterdata/UnitUnit.json'),
        parameters=load('masterdata/UnitUnitParameter.json'),
        initials=load('masterdata/UnitInitialParam.json'),
        jobs=load('masterdata/UnitJob.json'),
        types_data=load('masterdata/UnitTypeParameter.json'),
        evos=load('masterdata/UnitEvolutionPattern.json'),
        ud=load('masterdata/ComposeMaxUnityValueSetting.json'),
    )

    if not unit_ids:
        print('dumping to composed.json')
        output = loader.dump_raw()
        with open('composed.json', mode='w', encoding='utf8') as fd:
            json.dump(output, fd, indent='\t', ensure_ascii=False)
    else:
        for unit_id in unit_ids:
            unit = loader.load_unit(int(unit_id))
            print(unit)


def load(fn: str) -> list:
    with open(fn, mode='r', encoding='utf8') as fd:
        return json.load(fd)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
