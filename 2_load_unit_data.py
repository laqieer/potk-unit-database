# -*- coding:utf-8 -*-
from potk_unit_extractor.loader import load_folder
from pathlib import Path
import json


def main(unit_ids: list):
    loader = load_folder(Path('masterdata'))
    if not unit_ids:
        print('dumping to composed.json')
        output = loader.dump_raw()
        with open('composed.json', mode='w', encoding='utf8') as fd:
            json.dump(output, fd, indent='\t', ensure_ascii=False)
    else:
        for unit_id in unit_ids:
            unit = loader.load_unit(int(unit_id))
            print(unit)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
