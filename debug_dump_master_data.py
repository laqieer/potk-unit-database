# -*- coding:utf-8 -*-
# Python script for debug purposes, dump all master data assets into JSON format
#
# Takes the cache path and the output path as arguments.
from potk_unit_extractor.master_data import MasterData, MasterDataRepo
from pathlib import Path
import json


if __name__ == '__main__':
    import sys

    repo = MasterDataRepo(Path(sys.argv[1]))
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(exist_ok=True)

    for md in MasterData:
        print(f'Reading {md.name}')
        contents = repo.read(md)
        print(f'  Read {len(contents)} items')
        json_path = out_dir / f'{md.name}.json'
        with json_path.open(mode='w', encoding='utf-8') as fd:
            json.dump(contents, fd, indent='\t', ensure_ascii=False)
        print(f'  Saved to {json_path}')
