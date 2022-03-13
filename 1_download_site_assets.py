# -*- coding:utf-8 -*-
# Python script to download only the assets necessary to extract unit data
# (Stats caps, skills, etc).
#
# Takes the paths.json file as an argument.
# Saves all files to the current working directory.
import os

import click

from potk_unit_extractor.site import SiteManager


@click.command()
@click.argument('paths_fp', nargs=1)
@click.argument('unit_ids', nargs=-1)
@click.option('--no-remote', is_flag=True, default=False)
def main(paths_fp, unit_ids: list, no_remote: bool = False):
    mgr = SiteManager(work='.', sources=os.path.dirname(__file__))
    mgr.download_assets(paths_fp, unit_ids, no_remote, click.echo)


if __name__ == "__main__":
    main()
