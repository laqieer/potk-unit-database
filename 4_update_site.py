# -*- coding:utf-8 -*-
import hashlib
import json
import re
from pathlib import Path
from typing import Tuple, Set, Optional

import click
import requests

from potk_unit_extractor.loader import load_folder

CHECKSUMS_FN = 'checksums.json'
REMOTE_SITE = 'https://potk-fan-database.neocities.org'
REMOTE_SUMS_URL = f'{REMOTE_SITE}/{CHECKSUMS_FN}'


class Uploader:
    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
        self._auth_headers = {'Authorization': f'Bearer {api_key}'}
        self._session = requests.Session()

    def upload(self, local: Path, remote: str) -> requests.Response:
        r = self._session.post(
            f'{self._base_url}/api/upload',
            files={remote: local.open(mode='rb')},
            headers=self._auth_headers,
        )
        r.raise_for_status()
        return r


class UploadNarrator:
    def __init__(self):
        self._loader = load_folder(Path('cache', 'current'))
        self._unit_page_re = re.compile('units/([0-9]+).html$')

    def echo(self, local, remote, is_dry=False, *args, **kwargs):
        local_desc = self._desc(local)
        msg = f'Uploading {local_desc} to {REMOTE_SITE}/{remote}... '
        if is_dry:
            click.echo(f'[DRY-RUN] {msg}', *args, **kwargs)
        else:
            click.echo(msg, *args, **kwargs)

    def _desc(self, fn) -> str:
        m = self._unit_page_re.search(self._fn_to_str(fn))
        if m:
            return self._loader.load_unit(int(m.group(1))).h_id
        return str(fn)

    @staticmethod
    def _fn_to_str(fn) -> str:
        try:
            return fn.as_posix()
        except AttributeError:
            return str(fn)


def compute_local_sums(site_path: Path) -> Set[Tuple[str, str]]:
    result = set()
    for p in (p for p in site_path.rglob('*') if p.is_file()):
        fn = p.relative_to(site_path).as_posix()
        if fn == CHECKSUMS_FN:
            continue
        with p.open(mode='rb') as fp:
            md5 = hashlib.md5(fp.read()).hexdigest()
        result.add((fn, md5))  # tuples
    return result


def fetch_remote_sums(remote_sums_url: str) -> Set[Tuple[str, str]]:
    resp = requests.get(remote_sums_url)
    if resp.status_code == requests.codes.not_found:
        return set()
    resp.raise_for_status()
    # Assume a list of lists.
    return {tuple(item) for item in resp.json()}


@click.command()
@click.option('--site-path', default='./site')
@click.option('--api-key', '-k', default='')
@click.option('--dry-run', '-n', type=bool, default=False, is_flag=True)
def main(site_path: str, api_key: str, dry_run: bool):
    # Change parameters types.
    site_path: Path = Path(site_path)
    if not api_key:
        api_key = Path.home() / '.config/neocities/config'
        try:
            api_key = api_key.read_text(encoding='utf-8')
        except FileNotFoundError:
            click.echo(f'[WARNING] Unable to read api key ({api_key})')
            api_key = ''
    local_sums_path = site_path / CHECKSUMS_FN

    click.echo('Computing local checksums...')
    local_sums = compute_local_sums(site_path)
    with local_sums_path.open(mode='w', encoding='utf-8') as fp:
        json.dump(sorted(local_sums), fp, ensure_ascii=False)

    click.echo('Fetching remote checksums...')
    remote_sums = fetch_remote_sums(REMOTE_SUMS_URL)

    changed = local_sums - remote_sums
    click.echo(f'{len(changed)} files to be uploaded')

    if not changed:
        click.echo('Nothing to upload, site is up to date')
        return

    narrator = UploadNarrator()

    if dry_run:
        for fn, new_md5 in sorted(changed):
            narrator.echo(fn, fn, is_dry=True)
        click.echo(f'[DRY-RUN] Uploaded {len(changed)} files')
        return

    uploader = Uploader(base_url='https://neocities.org/', api_key=api_key)
    for fn, _ in sorted(changed):
        local = site_path / fn
        remote = Path(fn).as_posix()
        narrator.echo(local, remote, nl=False)
        r = uploader.upload(local, remote)
        click.echo(f'{r.status_code} {r.json()["result"].upper()}')

    click.echo(
        'Files uploaded successfully. Updating remote checksums file...  ',
        nl=False)
    r = uploader.upload(local_sums_path, CHECKSUMS_FN)
    click.echo(f'{r.status_code} {r.json()["result"].upper()}')
    click.echo('Site updated successfully')


if __name__ == '__main__':
    main()
