# -*- coding:utf-8 -*-
import hashlib
import json
from pathlib import Path
from typing import Tuple, Set

import requests

CHECKSUMS_FN = 'checksums.json'


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


def main(site_path: Path, remote_sums_url: str, api_key: str):
    local_sums_path = site_path / CHECKSUMS_FN

    print('Computing local checksums...')
    local_sums = compute_local_sums(site_path)
    with local_sums_path.open(mode='w', encoding='utf-8') as fp:
        json.dump(sorted(local_sums), fp, ensure_ascii=False)

    print('Fetching remote checksums...')
    remote_sums = fetch_remote_sums(remote_sums_url)

    changed = local_sums - remote_sums
    print(f'{len(changed)} files to be uploaded')

    if not changed:
        print('Nothing to upload, site is up to date')
        return

    uploader = Uploader(base_url='https://neocities.org/', api_key=api_key)
    for fn, _ in sorted(changed):
        local = site_path / fn
        remote = Path(fn).as_posix()
        print(f'Uploading {local} to {remote}...  ', end='')
        r = uploader.upload(local, remote)
        print(f'{r.status_code} {r.json()["result"].upper()}')

    print(
        'Files uploaded successfully. Updating remote checksums file...  ',
        end='')
    r = uploader.upload(local_sums_path, CHECKSUMS_FN)
    print(f'{r.status_code} {r.json()["result"].upper()}')
    print('Site updated successfully')


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 2:
        api_key_str = sys.argv[1]
    else:
        api_key_str = Path.home() / '.config' / 'neocities' / 'config'
        api_key_str = api_key_str.read_text(encoding='utf-8')
    main(
        Path('site'),
        f'https://potk-fan-database.neocities.org/{CHECKSUMS_FN}',
        api_key_str
    )
