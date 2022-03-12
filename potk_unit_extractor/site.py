# -*- coding: utf-8 -*-
import datetime
import hashlib
import heapq
import json
import math
import os
import re
import shutil
import time
from collections import defaultdict
from operator import attrgetter
from pathlib import Path
from typing import Iterable, Optional, List, Tuple, Set

import htmlmin
import js2py
import requests
from jinja2 import Template, FileSystemLoader, select_autoescape, Environment as JinjaEnv

from potk_unit_extractor.api import Environment
from potk_unit_extractor.loader import load_folder
from potk_unit_extractor.master_data import MasterDataRepo, MasterData
from potk_unit_extractor.model import SkillType, Skill, UnitData, StatType, UnitType, ClassChangeType, \
    SkillAwakeCategory, UnitTagKind, Element


def download_to_cache(paths_fp):
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


SKILL_ICON_RE = re.compile('images/skills/(\\d*)\\.png$')
UNIT_ASSETS_RE = re.compile('images/units/(\\d*)/.*\\.png$')


def fetch_remote_files_set(remote_sums_url: str):
    resp = requests.get(remote_sums_url)
    if resp.status_code == requests.codes.not_found:
        return set()
    resp.raise_for_status()
    return {i[0] for i in resp.json()}


def download_skills(ids: Iterable, env: Environment, assets: dict, existing_ids: set = None):
    target = Path('.', 'site', 'images', 'skills')
    target.mkdir(exist_ok=True, parents=True)

    seen = set(existing_ids) if existing_ids else set()
    for res_id in ids:
        if res_id in seen:
            continue
        seen.add(res_id)

        key = f'BattleSkills/{res_id}/skill_icon'
        if key in assets:
            icon_path = target / f'{res_id}.png'
            env.save_asset_icon(fn=assets[key][0], icon_path=icon_path)

    for extra in ['ability', 'def', 'leader', 'supply']:
        key = f'BattleSkills/{extra}_skill_icon'
        if key in assets:
            path = target / f'{extra}.png'
            env.save_asset_icon(fn=assets[key][0], icon_path=path)


def download_units(units: Iterable, env: Environment, streaming_assets: dict, existing_ids: set = None):
    target = Path('.', 'site', 'images', 'units')
    target.mkdir(exist_ok=True, parents=True)

    seen = set(existing_ids) if existing_ids else set()
    for unit in units:
        asset_id = unit.resource_id
        if asset_id in seen:
            continue
        seen.add(asset_id)

        unit_asset_path = target / str(asset_id)
        unit_asset_path.mkdir(exist_ok=True, parents=True)

        thumb_key = f'AssetBundle/Resources/Units/{asset_id}/2D/c_thum'
        if thumb_key in streaming_assets:
            env.save_streaming_asset(
                streaming_assets[thumb_key], thumb_key, unit_asset_path, True)

        hires_key = f'AssetBundle/Resources/Units/{asset_id}/2D/unit_hires'
        if hires_key in streaming_assets:
            env.save_streaming_asset(
                streaming_assets[hires_key], hires_key, unit_asset_path, True)


def download_assets(paths_fp, unit_ids: list, no_remote: bool, printer):
    printer("Loading file: " + paths_fp)
    with open(paths_fp, mode='rb') as fd:
        paths = json.load(fd)

    printer("Loading current cache")
    loader = load_folder(Path('cache', 'current'))

    if not no_remote:
        printer("Fetching remote file lists")
        remote_files = fetch_remote_files_set(
            'https://potk-fan-database.neocities.org/checksums.json')
    else:
        printer("Skipping remote file lists (--no-remote)")
        remote_files = set()

    remote_skills_ids = {
        int(m.group(1))
        for m in map(SKILL_ICON_RE.match, remote_files)
        if m
    }
    remote_units_ids = {
        int(m.group(1))
        for m in map(UNIT_ASSETS_RE.match, remote_files)
        if m
    }

    env = Environment(review_app_connect=True)
    streaming_assets: dict = paths['StreamingAssets']
    asset_bundle: dict = paths['AssetBundle']

    printer("Downloading Skills")
    skills = (s.resource_id or s.ID for s in loader.skills_repo.all_skills)
    download_skills(skills, env, asset_bundle, remote_skills_ids)

    printer("Downloading Units Assets")
    if unit_ids:
        units_gen = (loader.load_unit(int(i)) for i in unit_ids)
    else:
        units_gen = loader.load_playable_units()
    download_units(units_gen, env, streaming_assets, remote_units_ids)

    printer('All files downloaded')




class Progress:
    def __init__(self, total: int):
        self.total = total
        self.curr = 0
        self.last = time.time()

    def inc(self):
        self.curr += 1
        now = time.time()
        if now - self.last > 5:
            print(f'  {self.curr}/{self.total}')
            self.last = now


def sort_units(units: list):
    # Python sorting preserves original order.
    # Python sorting also is efficient on consecutive sorting.
    units.sort(key=attrgetter('ID'), reverse=True)
    units.sort(key=attrgetter('tags', 'any_name'))
    units.sort(key=attrgetter('published_at'), reverse=True)
    return units


def group_units(units: list, key: callable, iter_key: bool = False) -> dict:
    result = defaultdict(list)
    for unit in units:
        key_val = key(unit)
        if iter_key:
            for item in key_val:
                result[item].append(unit)
        else:
            result[key_val].append(unit)
    return result


def expand_unit(unit: UnitData) -> List[UnitData]:
    result: List[UnitData] = [unit]
    while unit.evolved_from:
        result.append(unit.evolved_from)
        unit = unit.evolved_from
    return list(reversed(result))


def compute_latest_releases(sorted_units: List[UnitData]) -> Iterable[Tuple]:
    releases = group_units(sorted_units, key=attrgetter('published_at'))
    last_3 = heapq.nlargest(3, releases.keys())
    return zip(last_3, (releases[k] for k in last_3))


def get_skill_icon_name(skill: Skill) -> Optional[str]:
    # CC Skills (ability) are handled on the template.
    if skill.type == SkillType.LEADER:
        return 'leader'
    elif skill.type == SkillType.ITEM:
        return 'supply'
    elif skill.type == SkillType.MAGIC:
        # TODO Use bullet icons
        return None
    else:
        rid = skill.resource_id or skill.ID
        return f'{rid}'


def render(template: Template, out: Path, minify: bool, **render_args):
    html = template.render(**render_args)
    if minify:
        html = htmlmin.minify(html)
    with out.open(mode='w', encoding='utf-8', newline='\n') as fp:
        fp.write(html)


def render_site(minify: bool, clean: bool, unit_ids: list):
    exec_start = datetime.datetime.now()
    print('Loading Units...')
    loader = load_folder(Path('cache', 'current'))
    env = JinjaEnv(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html']),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    site_path = Path('site')
    site_path.mkdir(exist_ok=True)

    units_path = site_path / 'units'
    tags_path = site_path / 'tags'
    skills_path = site_path / 'skills'
    flex_search_path = site_path / 'search'

    if clean:
        shutil.rmtree(units_path, ignore_errors=True)
        shutil.rmtree(tags_path, ignore_errors=True)
        shutil.rmtree(skills_path, ignore_errors=True)
        shutil.rmtree(flex_search_path, ignore_errors=True)
        shutil.rmtree(site_path / 'weapons', ignore_errors=True)
        shutil.rmtree(site_path / 'elements', ignore_errors=True)

    units_path.mkdir(exist_ok=True)
    tags_path.mkdir(exist_ok=True)
    skills_path.mkdir(exist_ok=True)
    flex_search_path.mkdir(exist_ok=True)

    def stars(unit: UnitData, final: UnitData) -> str:
        """★☆"""
        blank = final.rarity.stars_count - unit.rarity.stars_count
        return '★' * unit.rarity.stars_count + '☆' * blank

    # TODO Remove and use t.jp_ch directly
    jp_types = {t: t.jp_ch for t in UnitType}

    jp_stats = {
        StatType.HP:  '',
        StatType.STR: '力',
        StatType.MGC: '魔',
        StatType.GRD: '守',
        StatType.SPR: '精',
        StatType.SPD: '速',
        StatType.TEC: '技',
        StatType.LCK: '運',
    }

    cc_desc = {
        ClassChangeType.NORMAL:  '6★',
        ClassChangeType.VERTEX1: 'Vertex 1',
        ClassChangeType.VERTEX2: 'Vertex 2',
        ClassChangeType.VERTEX3: 'Vertex 3',
    }

    badge_tag = {
        UnitTagKind.LARGE:      'badge-danger',
        UnitTagKind.SMALL:      'badge-warning',
        UnitTagKind.CLOTHING:   'badge-primary',
        UnitTagKind.GENERATION: 'badge-dark',
        UnitTagKind.CUSTOM:     'badge-success',
    }

    badge_element = {
        Element.NONE:    'badge-secondary',
        Element.FIRE:    'badge-danger',
        Element.ICE:     'badge-primary',
        Element.WIND:    'badge-success',
        Element.THUNDER: 'badge-warning',
        Element.LIGHT:   'badge-light',
        Element.DARK:    'badge-dark',
    }

    category_desc = {
        SkillAwakeCategory.TRUST:           'Trust',
        SkillAwakeCategory.GENERIC_RS:      'Global RS',
        SkillAwakeCategory.CHAOS_RS:        'Chaos RS',
        SkillAwakeCategory.HARMONIA_RS:     'Harmonia RS',
        SkillAwakeCategory.TREISEMA_RS:     'Treisema RS',
        SkillAwakeCategory.TYRHELM_RS:      'Tyrhelm RS',
        SkillAwakeCategory.COMMAND_RS:      'Command Gear',
        SkillAwakeCategory.INTEGRAL_GEAR:   'Integral Gear',
        SkillAwakeCategory.SCHOOL_GEAR:     'School Gear',
        SkillAwakeCategory.IMITATE_GEAR:    'Imitate Gear',
        SkillAwakeCategory.FOURTH_RAGNAROK: 'Fourth Ragnarok',
    }

    category_comment = {
        SkillAwakeCategory.TRUST:
            ("Trust Skills are obtained from PoL Units. "
             "They're not faction locked, and can only be used by PoL Units."),
        SkillAwakeCategory.GENERIC_RS:
            ("Global Resonance Skills available to every unit that has an "
             "RS Slot. Cannot be used by pure PoL Units, but can be used by "
             "LR PoL units."),
        SkillAwakeCategory.CHAOS_RS:
            ("Resonance Skills obtained from Lost Ragnarok units of the "
             "Chaos Lion Empire faction. "
             "Can only be use by Special units and Chaos Lion units."),
        SkillAwakeCategory.HARMONIA_RS:
            ("Resonance Skills obtained from Lost Ragnarok units of the "
             "Harmonia Pontificate faction. "
             "Can only be use by Special units and Harmonia units."),
        SkillAwakeCategory.TREISEMA_RS:
            ("Resonance Skills obtained from Lost Ragnarok units of the "
             "Treisema Republic faction. "
             "Can only be use by Special units and Treisema units."),
        SkillAwakeCategory.TYRHELM_RS:
            ("Resonance Skills obtained from Lost Ragnarok units of the "
             "Tyrhelm faction. "
             "Can only be use by Special units and Tyrhelm units."),
        SkillAwakeCategory.COMMAND_RS:
            ("Resonance Skills obtained from Command Killers. "
             "Can only be use by Special units and Command Killers."),
        SkillAwakeCategory.INTEGRAL_GEAR:
            ("Gear Skills obtained from Integral Killers. "
             "Can only be use by Special units and Integral Killers."),
        SkillAwakeCategory.SCHOOL_GEAR:
            ("Gear Skills obtained from School Units. "
             "Can only be use by School Units."),
        SkillAwakeCategory.IMITATE_GEAR:
            ("Gear Skills obtained from Imitate Killers. "
             "Can only be use by Special units and Imitate Killers."),
    }

    if unit_ids:
        units = [loader.load_unit(int(u)) for u in unit_ids]
    else:
        units = [u for u in loader.load_playable_units() if not u.can_evolve]

    print(f'Loaded {len(units)} units successfully')

    print(f'Computing groups...')
    sort_units(units)
    units_by_tag = group_units(units, key=lambda u: u.tags, iter_key=True)
    units_by_weapon = group_units(units, key=lambda u: u.gear_kind)
    units_by_element = group_units(units, key=lambda u: u.element)
    latest_releases = compute_latest_releases(units)
    skill_icons = {s.ID: get_skill_icon_name(s)
                   for s in loader.skills_repo.all_skills}

    ovk_units = [unit for unit in units if unit.skills.ovk]
    ovk_units = group_units(ovk_units, key=lambda u: u.any_name)
    ovk_units = sorted((name, units) for name, units in ovk_units.items())

    rs_units = {
        c: sorted(
            (u for u in units
             if u.skills.relationship
             if u.skills.relationship.category == c),
            key=attrgetter('any_name', 'ID')
        )
        for c in SkillAwakeCategory
    }

    print(f'Computing search index...')
    with open('./js/flexsearch-0.6.22.min.js', mode='r', encoding='utf-8') as fd:
        flex_js_code = fd.read()
    flex_search = js2py.eval_js(flex_js_code + '; FlexSearch')
    search_index = flex_search.create()
    for unit in units:
        search_index.add(unit.ID, unit.h_id)
    with (flex_search_path / 'units.index.txt').open(mode='w', encoding='utf-8') as fd:
        fd.write(search_index.export())

    template_shared_args = {
        'StatType':           StatType,
        'UnitType':           UnitType,
        'ClassChangeType':    ClassChangeType,
        'SkillAwakeCategory': SkillAwakeCategory,
        'stars':              stars,
        'jp_types':           jp_types,
        'jp_stats':           jp_stats,
        'cc_desc':            cc_desc,
        'category_desc':      category_desc,
        'category_comment':   category_comment,
        'badge_tag':          badge_tag,
        'badge_element':      badge_element,
        'tags':               sorted(units_by_tag.keys()),
        'weapons':            sorted(units_by_weapon.keys()),
        'elements':           sorted(units_by_element.keys()),
        'skill_icons':        skill_icons,
    }

    print(f'Rendering Units to {units_path}')
    progress = Progress(len(units))
    unit_template = env.get_template('unit.html')
    for unit in units:
        output_path = units_path / f'{unit.ID}.html'
        render(
            template=unit_template,
            out=output_path,
            minify=minify,
            final_unit=unit,
            units=expand_unit(unit),
            **template_shared_args,
        )
        progress.inc()

    print(f'Rendering Skills lists to {skills_path}')
    progress = Progress(len(rs_units.keys()) + 1)
    ovk_path = skills_path / 'overkillers.html'
    render(
        template=env.get_template('ovk-skill-list.html'),
        out=ovk_path,
        minify=minify,
        cd_root='..',
        unit_groups=ovk_units,
        **template_shared_args,
    )
    progress.inc()
    generic_rs_list_template = env.get_template('rs-skill-list.html')
    for category, cat_units in rs_units.items():
        cat_path = skills_path / f'{category.name.lower()}.html'
        render(
            template=generic_rs_list_template,
            out=cat_path,
            minify=minify,
            cd_root='..',
            category=category,
            units=cat_units,
            **template_shared_args,
        )
        progress.inc()

    print(f'Rendering Tags to {tags_path}')
    tag_template = env.get_template('tag.html')
    progress = Progress(len(units_by_tag.items()))
    for tag, tag_units in units_by_tag.items():
        sort_units(tag_units)
        output_path = tags_path / f'{tag.uid}.html'
        render(
            template=tag_template,
            out=output_path,
            minify=minify,
            tag=tag,
            units=tag_units,
            total=len(tag_units),
            **template_shared_args,
        )
        progress.inc()

    generic_list_template = env.get_template('generic-unit-list.html')

    def render_generic_template(unit_map: dict, sub_path: str):
        generic_path = site_path / sub_path
        generic_path.mkdir(exist_ok=True)
        print(f'Rendering {sub_path.title()} to {generic_path}')
        progress = Progress(len(unit_map.items()))
        for k, k_units in unit_map.items():
            sort_units(k_units)
            out_path = generic_path / f'{k.value}.html'
            render(
                template=generic_list_template,
                out=out_path,
                minify=minify,
                page_title=k.name,
                total=len(k_units),
                units=k_units,
                **template_shared_args,
            )
            progress.inc()

    render_generic_template(units_by_weapon, 'weapons')
    render_generic_template(units_by_element, 'elements')

    index_path = site_path / 'index.html'
    print(f'Rendering {index_path}')
    render(
        template=env.get_template('index.html'),
        out=index_path,
        minify=minify,
        units=units,
        latest_releases=latest_releases,
        total=len(units),
        **template_shared_args,
    )

    elapsed_time = datetime.datetime.now() - exec_start
    count_ovk = sum(len(units) for _, units in ovk_units)
    print(f'\nAll pages rendered successfully in {elapsed_time}')
    print(f'{len(units)} Units')
    print(f'{len(units_by_tag.keys())} Tags')
    print(f'{count_ovk} Overkiller Skills')




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
    def __init__(self, printer):
        self._loader = load_folder(Path('cache', 'current'))
        self._unit_page_re = re.compile('units/([0-9]+).html$')
        self._printer = printer

    def echo(self, local, remote, is_dry=False, *args, **kwargs):
        local_desc = self._desc(local)
        msg = f'Uploading {local_desc} to {REMOTE_SITE}/{remote}... '
        if is_dry:
            self._printer(f'[DRY-RUN] {msg}', *args, **kwargs)
        else:
            self._printer(msg, *args, **kwargs)

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


def merge_sums(local, remote) -> Set[Tuple[str, str]]:
    # Set of tuple -> dict
    remote = {k: v for k, v in remote}
    local = {k: v for k, v in local}
    remote.update(local)
    return {tuple(i) for i in remote.items()}


def upload_site(site_path: str, api_key: str, dry_run: bool, printer):
    # Change parameters types.
    site_path: Path = Path(site_path)
    if not api_key:
        api_key = Path.home() / '.config/neocities/config'
        try:
            api_key = api_key.read_text(encoding='utf-8')
        except FileNotFoundError:
            printer(f'[WARNING] Unable to read api key ({api_key})')
            api_key = ''
    final_sums_path = site_path / CHECKSUMS_FN

    printer('Computing local checksums...')
    local_sums = compute_local_sums(site_path)

    printer('Fetching remote checksums...')
    remote_sums = fetch_remote_sums(REMOTE_SUMS_URL)

    changed = local_sums - remote_sums
    printer(f'{len(changed)} files to be uploaded')

    final_sums = merge_sums(local_sums, remote_sums)
    with final_sums_path.open(mode='w', encoding='utf-8') as fp:
        json.dump(sorted(final_sums), fp, ensure_ascii=False)

    if not changed:
        printer('Nothing to upload, site is up to date')
        return

    narrator = UploadNarrator(printer)

    if dry_run:
        for fn, new_md5 in sorted(changed):
            narrator.echo(fn, fn, is_dry=True)
        printer(f'[DRY-RUN] Uploaded {len(changed)} files')
        return

    uploader = Uploader(base_url='https://neocities.org/', api_key=api_key)
    for fn, _ in sorted(changed):
        local = site_path / fn
        remote = Path(fn).as_posix()
        narrator.echo(local, remote, nl=False)
        r = uploader.upload(local, remote)
        printer(f'{r.status_code} {r.json()["result"].upper()}')

    printer(
        'Files uploaded successfully. Updating remote checksums file...  ',
        nl=False)
    r = uploader.upload(final_sums_path, CHECKSUMS_FN)
    printer(f'{r.status_code} {r.json()["result"].upper()}')
    printer('Site updated successfully')
