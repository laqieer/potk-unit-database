# -*- coding:utf-8 -*-
# Python script to parse asset bundles with PotK Unit data and convert
# those bundles into more friendly JSON files.

from potk_unit_extractor.master_data_parsers import *
from pathlib import Path
import json
import unitypack  # Tested with UnityPack 0.9.0


def convert_asset_bundle(fp: Path, parser: callable, output_fn: str):
    print(f'Converting {fp.name}...')
    raw_data = read_raw_asset_data(fp)
    parsed_data = MasterDataReader(raw_data).read_all(len(raw_data), parser)
    target = f'{output_fn}.json'
    with open(target, mode='w', encoding='utf8') as fd:
        json.dump(parsed_data, fd, indent='\t', ensure_ascii=False)
    print(f'{fp.name} saved to {target}')


def read_raw_asset_data(fp: Path):
    with fp.open(mode='rb') as fd:
        pack = unitypack.load(fd)
    return pack.assets[0].objects[2].read().script


if __name__ == "__main__":
    wd = Path('.')
    convert_asset_bundle(
        fp=wd.glob("MasterData_UnitUnit_*.unity3d").__next__(),
        parser=parse_unit_unit,
        output_fn='UnitUnit'
    )
    convert_asset_bundle(
        fp=wd.glob("MasterData_UnitUnitParameter_*.unity3d").__next__(),
        parser=parse_unit_parameters,
        output_fn='UnitUnitParameter'
    )
