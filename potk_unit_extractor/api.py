from pathlib import Path
from PIL import ImageOps
from .master_data import MasterData
import urllib.request
import tempfile
import unitypack


class Environment:

    @property
    def dlc_url_base(self):
        return "/{0}".format("2018")  # Application.unityVersion.Split('.')[0])

    def __init__(self, paths: dict = None, review_app_connect=False, printer=print):
        self._printer = printer
        self.paths = paths
        self.dlc_path = "https://{0}.gu3.jp/dlc/production{1}/{2}/".format(
            "punk-dlc-review" if review_app_connect else "punk-dlc",
            self.dlc_url_base,
            "windows"
        )

    def _download_asset(self, asset_type, asset_id):
        url = f"{self.dlc_path}{asset_type}/{asset_id}"
        return urllib.request.urlopen(url).read()

    def save_master_data(self, res: MasterData, out: Path):
        key = f'MasterData/{res.name}'
        bundle = self.paths['AssetBundle'][key]
        if not bundle:
            raise ValueError(res)

        with out.open(mode='wb') as fd:
            fd.write(self._download_asset('ab', bundle['FileName']))

    def save_streaming_asset(
            self,
            asset: dict,
            key: str,
            target: Path,
            skip_existing: bool = True):
        """Save an sa type asset, without conversions (not necessary)"""
        if not asset:
            raise ValueError(key + " has empty bundle")

        download_fn = asset['FileName']
        target_fn = key.split('/')[-1]
        ext = asset[1]
        target_fp = target / f'{target_fn}{ext}'
        if skip_existing and target_fp.exists():
            return

        self._printer(f'Saving "{key}" to "{target_fp}"...')
        with target_fp.open(mode='wb') as fd:
            fd.write(self._download_asset('sa', download_fn))

    def save_asset_icon(
            self, fn: str, icon_path: Path, skip_existing: bool = True):
        """Download and extract icons from unity3d bundles"""
        if skip_existing and icon_path.exists():
            return
        self._printer(f'Saving {fn} to {icon_path}...')
        with tempfile.TemporaryFile() as fp:
            fp.write(self._download_asset('ab', fn))
            fp.seek(0)
            pack = unitypack.load(fp)
        data = pack.assets[0].objects[2].read()
        icon = ImageOps.flip(data.image)
        with icon_path.open(mode='wb') as fd:
            icon.save(fd, format="png")
