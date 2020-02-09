from pathlib import Path
import urllib.request

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


def download_asset_bundle(
        env: Environment, bundle: dict, ab_name: str, target: Path):
    if not bundle:
        raise ValueError(ab_name + " has empty bundle")

    download_fn = bundle[0]
    target_fn = '_'.join(ab_name.split('/')[1:])
    target_fn = target_fn + '.' + download_fn.split('.')[-1]
    target_fp = target / target_fn

    print(f'Saving "{ab_name}" to "{target_fp}"...')
    with target_fp.open(mode='wb') as fd:
        fd.write(env.download_asset('ab', download_fn))


def download_streaming_asset(
        env: Environment, asset: dict, key: str, target: Path):
    if not asset:
        raise ValueError(key + " has empty bundle")

    download_fn = asset[0]
    target_fn = key.split('/')[-1]
    ext = asset[1]
    target_fp = target / f'{target_fn}{ext}'

    print(f'Saving "{key}" to "{target_fp}"...')
    with target_fp.open(mode='wb') as fd:
        fd.write(env.download_asset('sa', download_fn))
