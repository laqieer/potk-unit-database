# -*- coding:utf-8 -*-
# Python script to parse asset bundles with PotK Unit data and convert
# those bundles into more friendly JSON files.

from potk_unit_extractor.master_data_parsers import *
from pathlib import Path
import json
import unitypack  # Tested with UnityPack 0.9.0


def convert_asset_bundle(
        source_fp: Path, parser: callable, target_dir: Path, output_fn: str):
    print(f'Converting {source_fp.name}...')
    raw_data = read_raw_asset_data(source_fp)
    parsed_data = MasterDataReader(raw_data).read_all(len(raw_data), parser)
    target_fp = target_dir / f'{output_fn}.json'
    with target_fp.open(mode='w', encoding='utf8') as fd:
        json.dump(parsed_data, fd, indent='\t', ensure_ascii=False)
    print(f'{source_fp.name} saved to {target_fp}')


def read_raw_asset_data(fp: Path):
    with fp.open(mode='rb') as fd:
        pack = unitypack.load(fd)
    return pack.assets[0].objects[2].read().script


if __name__ == "__main__":
    src = Path('bundles')
    output_dir = Path('masterdata')
    output_dir.mkdir(exist_ok=True)

    conversions = [
        (
            "MasterData_UnitUnit_*.unity3d",
            'UnitUnit',
            parse_unit_unit
        ),
        (
            "MasterData_UnitUnitParameter_*.unity3d",
            'UnitUnitParameter',
            parse_unit_parameters
        ),
        (
            "MasterData_UnitInitialParam_*.unity3d",
            'UnitInitialParam',
            parse_unit_initial_parameters
        ),
    ]
    for glob, ofn, parser in conversions:
        source_fp = src.glob(glob).__next__()
        convert_asset_bundle(source_fp, parser, output_dir, ofn)
