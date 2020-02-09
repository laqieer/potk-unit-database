# -*- coding:utf-8 -*-
# Python script to download only the assets necessary to extract unit data
# (Stats caps, skills, etc).
#
# Takes the paths.json file as an argument.
# Saves all files to the current working directory.

from potk_unit_extractor.api import Environment
import json


def main(paths_fp):
    print("Loading file: " + paths_fp)
    with open(paths_fp, mode='rb') as fd:
        paths = json.load(fd)
    print("File loaded successfully")
    asset_bundle: dict = paths['AssetBundle']
    env = Environment(True)
    download_asset_bundle(env, asset_bundle, 'MasterData/UnitUnit')
    download_asset_bundle(env, asset_bundle, 'MasterData/UnitUnitParameter')
    print('All files downloaded')


def download_asset_bundle(env: Environment, asset_bundles: dict, ab_name: str):
    details = asset_bundles[ab_name]
    if not details:
        raise ValueError(ab_name + " not found in the assets")

    download_fn = details['FileName']
    target_fn = ab_name.replace('/', '_') + '_' + download_fn

    print(f'Saving "{ab_name}" to "{target_fn}"...')
    with open(target_fn, 'wb') as fd:
        fd.write(env.download_asset('ab', download_fn))


if __name__ == "__main__":
    import sys
    try:
        main(sys.argv[1])
    except ValueError as ex:
        print(ex, file=sys.stderr)
        exit(1)
