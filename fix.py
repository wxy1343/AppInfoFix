import os
import winreg
import argparse
import requests
import traceback
from appinfo import Appinfo
from pathlib import Path
from steam.core.manifest import DepotManifest

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--app-id', type=int)
parser.add_argument('-i', '--install-dir', type=str)
parser.add_argument('-l', '--launch', type=str)
parser.add_argument('-d', '--depot-id', type=str)
parser.add_argument('-m', '--manifest-gid', type=str)
parser.add_argument('-s', '--size', type=str)
parser.add_argument('-n', '--no-fix-config', action='store_true', default=False)

repo = 'wxy1343/ManifestAutoUpdate'


def get_steam_path():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam')
    return Path(winreg.QueryValueEx(key, 'SteamPath')[0])


def main(args=None):
    args = parser.parse_args(args)
    app_id = args.app_id or int(input('appid: '))
    install_dir = None
    launch = None
    if not args.no_fix_config:
        install_dir = args.install_dir or input('安装目录: ')
        launch = args.launch or input('启动进程: ')
    steam_path = get_steam_path()
    vdf = Appinfo(steam_path/'appcache/appinfo.vdf')
    app_info = vdf.parsedAppInfo[app_id]
    if install_dir and launch:
        app_info['sections']['appinfo']['config'] = {'installdir': install_dir, 'launch': {'0': {'executable': launch}}}
    depot_id_list = args.depot_id.split(',') if args.depot_id else []
    manifest_gid_list = args.manifest_gid.split(',') if args.manifest_gid else len(depot_id_list) * [None]
    size_list = args.size.split(',') if args.size else len(depot_id_list) * [None]
    depot_cache = steam_path / 'depotcache'
    manifest_info = dict()
    for depot_id, manifest_gid, size in zip(depot_id_list, manifest_gid_list, size_list):
        if not manifest_gid or not size:
            if manifest_gid:
                manifest_path = depot_cache / f'{depot_id}_{manifest_gid}.manifest'
                if not manifest_path.exists():
                    raise FileNotFoundError(manifest_path)
                manifest_path = str(manifest_path.absolute())
            else:
                if not depot_cache.exists():
                    raise FileNotFoundError('depotcache')
                manifest_list = []
                for i in depot_cache.iterdir():
                    if i.suffix == '.manifest' and i.name.split('_')[0] == str(depot_id):
                        manifest_list.append(i)
                if not manifest_list:
                    raise Exception(f'找不到清单: {depot_id}')
                if len(manifest_list) > 1:
                    manifest_list = sorted(manifest_list, key=lambda x: x.stat().st_mtime)
                manifest_path = manifest_list[0]
                manifest_path = str(manifest_path.absolute())
            with open(manifest_path, 'rb') as f:
                manifest = DepotManifest(f.read())
            if not manifest_gid:
                manifest_gid = str(manifest.gid)
            size = str(manifest.metadata.cb_disk_original)
        manifest_info[str(depot_id)] = (str(manifest_gid), str(size))
    if not manifest_info:
        manifest_list = []
        url = f'https://api.github.com/repos/{repo}/branches/{app_id}'
        r = requests.get(url)
        if 'commit' in r.json():
            # sha = r.json()['commit']['sha']
            url = r.json()['commit']['commit']['tree']['url']
            r = requests.get(url)
            if 'tree' in r.json():
                for i in r.json()['tree']:
                    if i['path'].endswith('.manifest'):
                        manifest_list.append(i['path'])
        if not depot_cache.exists():
            raise FileNotFoundError('depotcache')
        depot_cache_list = [i.name for i in depot_cache.iterdir()]
        for manifest in manifest_list:
            if manifest in depot_cache_list:
                with (depot_cache / manifest).open('rb') as f:
                    manifest = DepotManifest(f.read())
                depot_id = str(manifest.depot_id)
                manifest_gid = str(manifest.gid)
                size = str(manifest.metadata.cb_disk_original)
                manifest_info[depot_id] = (manifest_gid, size)
    app_info['sections']['appinfo']['depots'] = {}
    for depot_id, _ in manifest_info.items():
        manifest_gid, size = _
        print(f'depot: {depot_id}, manifest: {manifest_gid}, size: {size}')
        app_info['sections']['appinfo']['depots'][str(depot_id)] = {'manifests': {'public': str(manifest_gid)},
                                                                    'maxsize': str(size)}
    vdf.update_app(app_info)
    vdf.write_data()
    print('appinfo.vdf修复成功')
    print('重启steam生效')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
    except:
        traceback.print_exc()
    os.system('pause')
