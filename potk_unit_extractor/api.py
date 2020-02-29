from pathlib import Path
from PIL import ImageOps
import urllib.request
import tempfile
import unitypack

GAME = 'punk.gu3.jp'
ASSETS = 'production-punk.nativebase.gu3.jp'
LOG_COLLECTION_URL = "https://punk-logcollection-production.gu3.jp/punk.production.client"


class Environment:

    @property
    def dlc_url_base(self):
        return "/{0}".format("2018")  # Application.unityVersion.Split('.')[0])

    def __init__(self, review_app_connect=False):
        self.label = "review" if review_app_connect else "production"

        self.server_url = "https://{}.gu3.jp/".format(
            "review-game.punk" if review_app_connect else "punk"),
        self.native_base_url = "https://production-punk.nativebase.gu3.jp",
        self.log_collection_url = LOG_COLLECTION_URL
        self.client_error_api = "/api/v2/client/error",
        self.auth_api_prefix = "/auth",
        self.purchase_api_prefix = "/api/v2/charge",
        self.dlc_path = "https://{0}.gu3.jp/dlc/production{1}/{2}/".format(
            "punk-dlc-review" if review_app_connect else "punk-dlc",
            self.dlc_url_base,
            "windows"
        )

    def download_asset(self, asset_type, asset_id):
        url = f"{self.dlc_path}{asset_type}/{asset_id}"
        return urllib.request.urlopen(url).read()

    def save_asset_bundle(self, bundle: dict, ab_name: str, target_dir: Path):
        """Save an unity3d asset bundle without conversions"""
        if not bundle:
            raise ValueError(ab_name + " has empty bundle")

        download_fn = bundle[0]
        target_fn = '_'.join(ab_name.split('/')[1:])
        target_fn = target_fn + '.' + download_fn.split('.')[-1]
        target_fp = target_dir / target_fn

        # FIXME no printing in API calls.
        print(f'Saving "{ab_name}" to "{target_fp}"...')
        with target_fp.open(mode='wb') as fd:
            fd.write(self.download_asset('ab', download_fn))

    def save_streaming_asset(
            self,
            asset: dict,
            key: str,
            target: Path,
            skip_existing: bool = True):
        """Save an sa type asset, without conversions (not necessary)"""
        if not asset:
            raise ValueError(key + " has empty bundle")

        download_fn = asset[0]
        target_fn = key.split('/')[-1]
        ext = asset[1]
        target_fp = target / f'{target_fn}{ext}'
        if skip_existing and target_fp.exists():
            return

        # FIXME no printing in API calls.
        print(f'Saving "{key}" to "{target_fp}"...')
        with target_fp.open(mode='wb') as fd:
            fd.write(self.download_asset('sa', download_fn))

    def save_asset_icon(
            self, fn: str, icon_path: Path, skip_existing: bool = True):
        """Download and extract icons from unity3d bundles"""
        if skip_existing and icon_path.exists():
            return
        print(f'Saving {fn} to {icon_path}...')
        with tempfile.TemporaryFile() as fp:
            fp.write(self.download_asset('ab', fn))
            fp.seek(0)
            pack = unitypack.load(fp)
        data = pack.assets[0].objects[2].read()
        icon = ImageOps.flip(data.image)
        with icon_path.open(mode='wb') as fd:
            icon.save(fd, format="png")
