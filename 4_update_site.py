# -*- coding:utf-8 -*-

import click

from potk_unit_extractor.site import upload_site


@click.command()
@click.option('--site-path', default='./site')
@click.option('--api-key', '-k', default='')
@click.option('--dry-run', '-n', type=bool, default=False, is_flag=True)
def main(site_path: str, api_key: str, dry_run: bool):
    upload_site(site_path, api_key, dry_run, click.echo)


if __name__ == '__main__':
    main()
