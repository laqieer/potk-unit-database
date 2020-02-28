# -*- coding:utf-8 -*-
# Python script to download only the assets necessary to extract unit data
# (Stats caps, skills, etc).
#
# Takes the paths.json file as an argument.
# Saves all files to the current working directory.
from typing import Iterable
from potk_unit_extractor.loader import load_folder
from potk_unit_extractor.api import Environment, download_streaming_asset
from pathlib import Path
from PIL import ImageOps
import unitypack
import tempfile
import json


def download_skills(skills: Iterable, env: Environment, assets: dict):
    target = Path('.', 'site', 'images', 'skills')
    target.mkdir(exist_ok=True, parents=True)

    seen = set()
    for skill in skills:
        if skill in seen:
            continue
        seen.add(skill)

        icon_path = target / f'{skill}.png'
        if icon_path.exists():
            continue

        key = f'BattleSkills/{skill}/skill_icon'
        if key in assets:
            print(f'Downloading skill icon {skill}...')
            with tempfile.TemporaryFile() as fp:
                fp.write(env.download_asset('ab', assets[key][0]))
                fp.seek(0)
                pack = unitypack.load(fp)
            data = pack.assets[0].objects[2].read()
            icon = ImageOps.flip(data.image)
            with icon_path.open(mode='wb') as fd:
                icon.save(fd, format="png")


def download_units(units: Iterable, env: Environment, streaming_assets: dict):
    target = Path('.', 'site', 'images', 'units')
    target.mkdir(exist_ok=True, parents=True)

    seen = set()
    for unit in units:
        asset_id = unit.resource_id
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


def main(paths_fp, ids: list):
    print("Loading file: " + paths_fp)
    with open(paths_fp, mode='rb') as fd:
        paths = json.load(fd)
    print("File loaded successfully")
    env = Environment(True)
    streaming_assets: dict = paths['StreamingAssets']
    asset_bundle: dict = paths['AssetBundle']

    loader = load_folder(Path('masterdata'))

    download_skills(
        (s['resource_reference_id'] or s['ID'] for s in loader.skills.values()),
        env,
        asset_bundle)

    if ids:
        units_gen = (loader.load_unit(i) for i in ids)
    else:
        units_gen = loader.load_playable_units()

    download_units(units_gen, env, streaming_assets)

    print('All files downloaded')


if __name__ == "__main__":
    import sys

    try:
        main(sys.argv[1], [int(arg) for arg in sys.argv[2:]])
    except ValueError as ex:
        print(ex, file=sys.stderr)
        exit(1)
