# -*- coding:utf-8 -*-
# Python script to download only the assets necessary to extract unit data
# (Stats caps, skills, etc).
#
# Takes the paths.json file as an argument.
# Saves all files to the current working directory.

from pathlib import Path
from potk_unit_extractor.api import Environment, download_asset_bundle
from potk_unit_extractor.master_data import KNOWN_MASTER_DATA
import json
import shutil


def main(paths_fp):
    print("Loading file: " + paths_fp)
    with open(paths_fp, mode='rb') as fd:
        paths = json.load(fd)
    print("File loaded successfully")
    asset_bundle: dict = paths['AssetBundle']
    env = Environment(True)
    target = Path('.', 'bundles')
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir()

    for md in KNOWN_MASTER_DATA:
        name = "MasterData/" + md.name
        download_asset_bundle(env, asset_bundle[name], name, target)

    print('All files downloaded')


if __name__ == "__main__":
    import sys

    try:
        main(sys.argv[1])
    except ValueError as ex:
        print(ex, file=sys.stderr)
        exit(1)
