# -*- coding:utf-8 -*-
import os

import click

from potk_unit_extractor.site import SiteManager


@click.command()
@click.option('--minify', is_flag=True, default=False)
@click.option('--clean', is_flag=True, default=False)
@click.argument('unit_ids', nargs=-1)
def main(minify: bool, clean: bool, unit_ids: list):
    mgr = SiteManager(work='.', sources=os.path.dirname(__file__))
    mgr.render_site(minify, clean, unit_ids)


if __name__ == '__main__':
    main()
