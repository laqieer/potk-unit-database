# -*- coding:utf-8 -*-
import os

import click

from potk_unit_extractor.site import SiteManager


@click.command()
@click.option('--site-path', default='./site')
@click.option('--api-key', '-k', default='')
@click.option('--dry-run', '-n', type=bool, default=False, is_flag=True)
def main(site_path: str, api_key: str, dry_run: bool):
    mgr = SiteManager(
        work='.',
        sources=os.path.dirname(__file__),
        printer=click.echo,
    )
    mgr.upload_site(site_path, api_key, dry_run)


if __name__ == '__main__':
    main()
