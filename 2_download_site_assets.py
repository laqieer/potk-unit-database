# -*- coding:utf-8 -*-
# Python script to download only the assets necessary to extract unit data
# (Stats caps, skills, etc).
#
# Takes the paths.json file as an argument.
# Saves all files to the current working directory.

from potk_unit_extractor.loader import load_folder
from potk_unit_extractor.api import Environment, download_streaming_asset
from pathlib import Path
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

    loader = load_folder(Path('masterdata'))
    assets = [unit.resource_id for unit in loader.load_playable_units()]

    seen = set()
    for asset_id in assets:
        if asset_id in seen:
            continue
        seen.add(asset_id)

        unit_asset_path = target / str(asset_id)
        unit_asset_path.mkdir(exist_ok=True, parents=True)

        thumb_key = f'AssetBundle/Resources/Units/{asset_id}/2D/c_thum'
        if thumb_key in streaming_assets:
            download_streaming_asset(
                env, streaming_assets[thumb_key], thumb_key, unit_asset_path)

        hires_key = f'AssetBundle/Resources/Units/{asset_id}/2D/unit_hires'
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
