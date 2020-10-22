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
import requests
import re
import click

SKILL_ICON_RE = re.compile('images/skills/(\\d*)\\.png$')
UNIT_ASSETS_RE = re.compile('images/units/(\\d*)/.*\\.png$')


def fetch_remote_files_set(remote_sums_url: str):
    resp = requests.get(remote_sums_url)
    if resp.status_code == requests.codes.not_found:
        return set()
    resp.raise_for_status()
    return {i[0] for i in resp.json()}


def download_skills(ids: Iterable, env: Environment, assets: dict, existing_ids: set = None):
    target = Path('.', 'site', 'images', 'skills')
    target.mkdir(exist_ok=True, parents=True)

    seen = set(existing_ids) if existing_ids else set()
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


def download_units(units: Iterable, env: Environment, streaming_assets: dict, existing_ids: set = None):
    target = Path('.', 'site', 'images', 'units')
    target.mkdir(exist_ok=True, parents=True)

    seen = set(existing_ids) if existing_ids else set()
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
                streaming_assets[thumb_key], thumb_key, unit_asset_path, True)

        hires_key = f'AssetBundle/Resources/Units/{asset_id}/2D/unit_hires'
        if hires_key in streaming_assets:
            env.save_streaming_asset(
                streaming_assets[hires_key], hires_key, unit_asset_path, True)


@click.command()
@click.argument('paths_fp', nargs=1)
@click.argument('unit_ids', nargs=-1)
@click.option('--no-remote', is_flag=True, default=False)
def main(paths_fp, unit_ids: list, no_remote: bool = False):
    click.echo("Loading file: " + paths_fp)
    with open(paths_fp, mode='rb') as fd:
        paths = json.load(fd)

    click.echo("Loading current cache")
    loader = load_folder(Path('cache', 'current'))

    if not no_remote:
        click.echo("Fetching remote file lists")
        remote_files = fetch_remote_files_set(
            'https://potk-fan-database.neocities.org/checksums.json')
    else:
        click.echo("Skipping remote file lists (--no-remote)")
        remote_files = set()

    remote_skills_ids = {
        int(m.group(1))
        for m in map(SKILL_ICON_RE.match, remote_files)
        if m
    }
    remote_units_ids = {
        int(m.group(1))
        for m in map(UNIT_ASSETS_RE.match, remote_files)
        if m
    }

    env = Environment(review_app_connect=True)
    streaming_assets: dict = paths['StreamingAssets']
    asset_bundle: dict = paths['AssetBundle']

    click.echo("Downloading Skills")
    skills = (s.resource_id or s.ID for s in loader.skills_repo.all_skills)
    download_skills(skills, env, asset_bundle, remote_skills_ids)

    click.echo("Downloading Units Assets")
    if unit_ids:
        units_gen = (loader.load_unit(int(i)) for i in unit_ids)
    else:
        units_gen = loader.load_playable_units()
    download_units(units_gen, env, streaming_assets, remote_units_ids)

    click.echo('All files downloaded')


if __name__ == "__main__":
    main()
