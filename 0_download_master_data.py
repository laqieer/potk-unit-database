# -*- coding:utf-8 -*-
# Python script to download only the assets necessary to extract unit data
# (Stats caps, skills, etc).
#
# Takes the paths.json file as an argument.
# Saves the downloaded assets into ./cache/
import json
import math
import os
import shutil
from pathlib import Path

from potk_unit_extractor.api import Environment
from potk_unit_extractor.master_data import MasterDataRepo, MasterData


def main(paths_fp):
    print("Loading file: " + paths_fp)
    with open(paths_fp, mode='rb') as fd:
        paths = json.load(fd)
    print("File loaded successfully")
    env = Environment(paths, True)

    root_path = Path('.', 'cache', 'current')
    if root_path.exists():  # FIXME Ask for forgiveness
        shutil.rmtree(root_path)
    repo = MasterDataRepo(root_path)

    for md in MasterData:
        md_path = repo.path_of(md)
        print(f'Saving {md.name} to {md_path}...')
        env.save_master_data(res=md, out=md_path)

    print('All files downloaded')

    paths_date = os.path.getmtime(paths_fp)
    history_path = Path('.', 'cache', str(math.trunc(paths_date)))
    if history_path.exists():
        print('WARNING: History path already exists, no backup will be created')
        return
    shutil.copytree(root_path, history_path)
    print(f'History backup at: {history_path}')


if __name__ == "__main__":
    import sys

    try:
        main(sys.argv[1])
    except ValueError as ex:
        print(ex, file=sys.stderr)
        exit(1)
