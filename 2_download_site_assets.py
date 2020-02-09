# -*- coding:utf-8 -*-
# Python script to download only the assets necessary to extract unit data
# (Stats caps, skills, etc).
#
# Takes the paths.json file as an argument.
# Saves all files to the current working directory.

from pathlib import Path
from potk_unit_extractor.api import Environment, download_asset_bundle, \
    download_streaming_asset
import json


def main(paths_fp):
    print("Loading file: " + paths_fp)
    with open(paths_fp, mode='rb') as fd:
        paths = json.load(fd)
    print("File loaded successfully")
    streaming_assets: dict = paths['StreamingAssets']
    env = Environment(True)
    target = Path('.', 'site', 'images', 'units')
    target.mkdir(exist_ok=True, parents=True)

    with open('masterdata/UnitUnit.json', mode='r', encoding='utf8') as fd:
        units = json.load(fd)

    seen = set()
    for unit in units:
        unit_id = unit['resource_reference_unit_id_UnitUnit']
        if unit_id in seen:
            continue
        seen.add(unit_id)

        unit_asset_path = target / str(unit_id)
        unit_asset_path.mkdir(exist_ok=True, parents=True)

        thumb_key = f'AssetBundle/Resources/Units/{unit_id}/2D/c_thum'
        if thumb_key in streaming_assets:
            download_streaming_asset(
                env, streaming_assets[thumb_key], thumb_key, unit_asset_path)

        hires_key = f'AssetBundle/Resources/Units/{unit_id}/2D/unit_hires'
        if hires_key in streaming_assets:
            download_streaming_asset(
                env, streaming_assets[hires_key], hires_key, unit_asset_path)

    print('All files downloaded')


if __name__ == "__main__":
    import sys

    try:
        main(sys.argv[1])
    except ValueError as ex:
        print(ex, file=sys.stderr)
        exit(1)
