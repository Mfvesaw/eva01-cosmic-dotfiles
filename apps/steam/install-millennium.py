#!/usr/bin/env python3
"""Install the verified Millennium release in this user's home, without sudo.

Uses the upstream MILLENNIUM_RUNTIME_PATH bootstrap override. Steam must be
fully exited and started again for the hook to load; this script never stops it.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import shutil
import tarfile

VERSION='3.6.2'
SHA256='95bda40184dd6437da1668060ec5961c762f3c1e59923f53380e43d4e720f359'
BASE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--home',type=Path,default=Path.home())
parser.add_argument('--dry-run',action='store_true')
args=parser.parse_args();home=args.home.expanduser().absolute()
if home==Path('/'):parser.error('Choose a user home directory.')
archive=BASE/f'millennium-v{VERSION}-linux-x86_64.tar.gz'
if hashlib.sha256(archive.read_bytes()).hexdigest()!=SHA256:
    raise SystemExit('Millennium archive checksum mismatch')
backup=home/'.local/state/eva01/steam-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
runtime=home/'.local/lib/millennium'/VERSION
steam=home/'.steam/steam'
if not steam.exists():steam=home/'.local/share/Steam'
if not steam.resolve().is_relative_to(home.resolve()):raise SystemExit('Steam must be installed inside this home.')
records=[]
def put(path,data,mode=0o644):
    if path.exists() and not path.is_symlink() and path.read_bytes()==data:return
    records.append(str(path.relative_to(home)))
    if args.dry_run:return
    old=backup/path.relative_to(home)
    if path.exists() or path.is_symlink():
        old.parent.mkdir(parents=True,exist_ok=True)
        if path.is_symlink():old.symlink_to(os.readlink(path))
        else:shutil.copy2(path,old)
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.eva01-tmp')
    if temp.is_symlink():temp.unlink()
    temp.write_bytes(data);temp.chmod(mode);os.replace(temp,path)
libs={}
with tarfile.open(archive) as tar:
    for member in tar:
        if not member.isfile():continue
        parts=Path(member.name).parts
        if parts[:3]!=('usr','lib','millennium') or len(parts)!=4:
            raise SystemExit('Unexpected Millennium release file: '+member.name)
        libs[parts[-1]]=tar.extractfile(member).read()
for name in ['libmillennium_x86.so','libmillennium_bootstrap_x86.so',
             'libmillennium_bootstrap_hhx64.so','libmillennium_hhx64.so',
             'libmillennium_pvs64','libmillennium_luavm_x86']:
    put(runtime/name,libs[name],0o755)
put(steam/'ubuntu12_32/libXtst.so.6',libs['libmillennium_bootstrap_x86.so'],0o755)
# Copies stay visible inside Steam's web-helper container.
put(steam/'ubuntu12_64/libXtst.so.6',libs['libmillennium_bootstrap_hhx64.so'],0o755)
put(steam/'ubuntu12_64/libmillennium_hhx64.so',libs['libmillennium_hhx64.so'],0o755)
wrapper=home/'.local/bin/steam'
put(wrapper,('''#!/bin/sh
# EVA01: user-local Millennium, with the original system Steam launcher.
export MILLENNIUM_RUNTIME_PATH="$HOME/.local/lib/millennium/3.6.2/libmillennium_x86.so"
exec /usr/bin/steam "$@"
''').encode(),0o755)
put(home/'.config/environment.d/80-eva01-steam.conf',
    b'MILLENNIUM_RUNTIME_PATH=${HOME}/.local/lib/millennium/3.6.2/libmillennium_x86.so\n')
put(home/'.config/fish/functions/steam.fish',b'''function steam --description 'Steam with the EVA01 user-local Millennium loader'
    if test -x ~/.local/bin/steam
        command ~/.local/bin/steam $argv
    else
        command /usr/bin/steam $argv
    end
end
''')
source=Path('/usr/share/applications/steam.desktop')
if source.exists():
    desktop=source.read_text().replace('Exec=/usr/bin/steam','Exec="'+str(wrapper)+'"')
else:
    desktop='[Desktop Entry]\nType=Application\nName=Steam\nExec="'+str(wrapper)+'" %U\nIcon=steam\nTerminal=false\nCategories=Game;\nMimeType=x-scheme-handler/steam;\n'
put(home/'.local/share/applications/steam.desktop',desktop.encode())
cfg=home/'.config/millennium/config.json'
data=json.loads(cfg.read_text()) if cfg.exists() else {}
data.setdefault('general',{})['injectCSS']=True
data.setdefault('themes',{}).update(activeTheme='EVA01',allowedStyles=True,allowedScripts=False)
put(cfg,(json.dumps(data,indent=2)+'\n').encode())
if not args.dry_run:
    backup.mkdir(parents=True,exist_ok=True)
    (backup/'manifest.json').write_text(json.dumps({'modified':records,'version':VERSION},indent=2)+'\n')
print(('Would install' if args.dry_run else 'Installed')+' Millennium '+VERSION+' in '+str(runtime))
print('Theme: EVA01. Fully quit Steam, then open Steam normally to load it.')
print('Previous files:',backup)
