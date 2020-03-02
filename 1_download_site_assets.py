# -*- coding:utf-8 -*-
# Python script to download only the assets necessary to extract unit data
# (Stats caps, skills, etc).
#
# Takes the paths.json file as an argument.
# Saves all files to the current working directory.
from typing import Iterable
from potk_unit_extractor.loader import load_folder
from potk_unit_extractor.api import Environment
from pathlib import Path
import json


def download_skills(ids: Iterable, env: Environment, assets: dict):
    target = Path('.', 'site', 'images', 'skills')
    target.mkdir(exist_ok=True, parents=True)

    seen = set()
    for res_id in ids:
        if res_id in seen:
            continue
        seen.add(res_id)

        key = f'BattleSkills/{res_id}/skill_icon'
        if key in assets:
            icon_path = target / f'{res_id}.png'
            env.save_asset_icon(fn=assets[key][0], icon_path=icon_path)

    for extra in ['ability', 'def', 'leader', 'supply']:
        key = f'BattleSkills/{extra}_skill_icon'
        if key in assets:
            path = target / f'{extra}.png'
            env.save_asset_icon(fn=assets[key][0], icon_path=path)


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
            env.save_streaming_asset(
                streaming_assets[thumb_key], thumb_key, unit_asset_path)

        hires_key = f'AssetBundle/Resources/Units/{asset_id}/2D/unit_hires'
        if hires_key in streaming_assets:
            env.save_streaming_asset(
                streaming_assets[hires_key], hires_key, unit_asset_path)


def main(paths_fp, ids: list):
    print("Loading file: " + paths_fp)
    with open(paths_fp, mode='rb') as fd:
        paths = json.load(fd)
    print("File loaded successfully")
    env = Environment(review_app_connect=True)
    streaming_assets: dict = paths['StreamingAssets']
    asset_bundle: dict = paths['AssetBundle']

    loader = load_folder(Path('cache'))

    download_skills(
        (s.skill_icon for s in loader.skills_repo.all_skills),
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
