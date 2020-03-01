# -*- coding:utf-8 -*-
# Python script to parse asset bundles with PotK Unit data and convert
# those bundles into more friendly JSON files.
from potk_unit_extractor.master_data import KNOWN_MASTER_DATA
from potk_unit_extractor.master_data_reader import MasterDataReader
from pathlib import Path
import json
import unitypack  # Tested with UnityPack 0.9.0


def run_conversions(assets):
    for md in assets:
        source_fp = src / f'{md.name}.unity3d'
        convert_asset_bundle(source_fp, md.parser, output_dir, md.name)


def convert_asset_bundle(
        source_fp: Path, parser: callable, target_dir: Path, output_fn: str):
    print(f'Converting {source_fp.name}...')
    raw_data = read_raw_asset_data(source_fp)
    print(f'  Read {len(raw_data)} bytes')
    parsed_data = MasterDataReader(raw_data).read_all(len(raw_data), parser)
    target_fp = target_dir / f'{output_fn}.json'
    with target_fp.open(mode='w', encoding='utf8') as fd:
        json.dump(parsed_data, fd, indent='\t', ensure_ascii=False)
    print(f'  {source_fp.name} saved to {target_fp}')


def read_raw_asset_data(fp: Path):
    with fp.open(mode='rb') as fd:
        pack = unitypack.load(fd)
    return pack.assets[0].objects[2].read().script


if __name__ == "__main__":
    src = Path('bundles')
    output_dir = Path('masterdata')
    output_dir.mkdir(exist_ok=True)

    run_conversions(KNOWN_MASTER_DATA)
