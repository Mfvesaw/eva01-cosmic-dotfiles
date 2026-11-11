#!/usr/bin/env python3
"""Restore the EVA01 desktop, backing up overwritten files first."""
from pathlib import Path, PurePosixPath
import argparse
import configparser
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dry-run', action='store_true', help='verify and list changes without writing anything')
parser.add_argument('--home', type=Path, default=Path.home(), help='restore into another home; skip desktop integration')
parser.add_argument('--dependencies', action='store_true', help='install Fedora terminal/Qt/font/KiCad packages using sudo dnf')
parser.add_argument('--apps', action='store_true', help='reinstall the saved Flatpak application inventory')
parser.add_argument('--wallpaper', choices=('eva01', 'purple-nebula'), default='eva01',
                    help='choose a bundled wallpaper (default: eva01)')
args = parser.parse_args()
home = args.home.expanduser().absolute()
if home == Path('/') or home == ROOT or ROOT.is_relative_to(home) and home != Path.home():
    parser.error('Choose a user home directory, outside the repository.')
desktop = home == Path.home()
if (args.dependencies or args.apps) and not desktop:
    parser.error('--dependencies/--apps can only be used for your actual home')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
backup = home/'.local/state/eva01/backups'/stamp
saved = set()
actions = []

def run(argv):
    print('+', ' '.join(map(str, argv)))
    if not args.dry_run: subprocess.run(list(map(str, argv)), check=True)

def verify():
    manifest = ROOT/'metadata/SHA256SUMS'
    if not manifest.exists(): raise SystemExit('Missing checksum manifest; backup is incomplete.')
    count = 0
    for line in manifest.read_text().splitlines():
        expected, relative = line.split('  ', 1)
        path = ROOT/relative
        if not path.resolve().is_relative_to(ROOT): raise SystemExit('Invalid checksum path')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit('Checksum mismatch: '+relative)
        count += 1
    print(f'Verified {count} backup files.')

def save(path):
    if path in saved: return
    if path.exists() or path.is_symlink():
        target = backup/path.relative_to(home)
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink(): target.symlink_to(os.readlink(path))
        elif path.is_dir(): shutil.copytree(path, target, symlinks=True)
        else: shutil.copy2(path, target)
    saved.add(path)

def content(path):
    raw = path.read_bytes()
    try: return raw.decode().replace('__EVA01_HOME__', str(home)).encode()
    except UnicodeError: return raw

def put(path, data, mode=0o644):
    if path.exists() and not path.is_symlink() and path.is_file() and path.read_bytes() == data:
        return
    actions.append(str(path.relative_to(home)))
    if args.dry_run: return
    save(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Replace symlinks rather than writing through to a shared or generated file.
    temp = path.with_name(path.name+'.eva01-tmp')
    if temp.is_symlink(): temp.unlink()
    temp.write_bytes(data); temp.chmod(mode); os.replace(temp, path)

def deep_merge(old, new):
    result = dict(old)
    for key, value in new.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else: result[key] = value
    return result

def jsonc(text):
    # Strip JSONC comments and trailing commas outside quoted strings.
    result=[]; i=0; quoted=False; escaped=False
    while i < len(text):
        ch=text[i]
        if quoted:
            result.append(ch)
            if escaped: escaped=False
            elif ch=='\\': escaped=True
            elif ch=='"': quoted=False
            i+=1; continue
        if ch=='"': quoted=True;result.append(ch);i+=1;continue
        if text.startswith('//',i):
            end=text.find('\n',i);i=len(text) if end<0 else end;continue
        if text.startswith('/*',i):
            end=text.find('*/',i+2)
            if end<0:raise ValueError('Unclosed JSONC comment')
            result.append(' ');i=end+2;continue
        result.append(ch);i+=1
    text=''.join(result);result=[];quoted=False;escaped=False
    for i,ch in enumerate(text):
        if quoted:
            result.append(ch)
            if escaped:escaped=False
            elif ch=='\\':escaped=True
            elif ch=='"':quoted=False
        elif ch=='"':quoted=True;result.append(ch)
        elif ch==',' and text[i+1:].lstrip().startswith(('}',']')):continue
        else:result.append(ch)
    return json.loads(''.join(result))

def merge_json(source, target):
    new=jsonc(content(source).decode())
    if target.exists():
        try: new=deep_merge(jsonc(target.read_text()),new)
        except (ValueError,UnicodeError) as error:
            raise SystemExit(f'Cannot safely merge {target}: {error}')
    put(target,(json.dumps(new,indent=2)+'\n').encode())

verify()
# Parse and validate every archive entry before changing any desktop files.
archive = ROOT/'assets/desktop-assets.tar.xz'
with tarfile.open(archive) as tar:
    members=tar.getmembers()
    for member in members:
        rel=PurePosixPath(member.name)
        if rel.is_absolute() or '..' in rel.parts or rel.parts[0] not in ('icons','themes','color-schemes'):
            raise SystemExit('Unsafe asset archive path: '+member.name)
        tarfile.data_filter(member, str(home/'.local/share'))
print(f'Asset archive validated ({len(members)} entries).')

if args.dependencies:
    if not shutil.which('dnf'): raise SystemExit('--dependencies currently supports Fedora/dnf.')
    run(['sudo','dnf','install','-y','fish','fastfetch','starship','qt5ct','qt6ct',
         'urw-base35-nimbus-mono-ps-fonts','kicad'])
if args.apps:
    if not shutil.which('flatpak'): raise SystemExit('Install Flatpak first.')
    # Exported signed remote definitions are restored without disabling GPG checks.
    for definition in sorted((ROOT/'metadata/remotes').glob('*.flatpakrepo')):
        run(['flatpak','remote-add','--user','--if-not-exists','--from',definition.stem,definition])
    for line in (ROOT/'metadata/flatpak-apps.tsv').read_text().splitlines():
        app,remote,branch=line.split('\t')
        run(['flatpak','install','--user','--noninteractive',remote,app+'//'+branch])

# Merge environment and Flatpak overrides to preserve unrelated user settings.
def merge_ini(source,target):
    new=configparser.ConfigParser(interpolation=None,strict=False);new.optionxform=str
    new.read_string(content(source).decode())
    old=configparser.ConfigParser(interpolation=None,strict=False);old.optionxform=str
    if target.exists():old.read(target)
    for section in new.sections():
        if not old.has_section(section):old.add_section(section)
        for key,value in new[section].items():
            if section=='Context' and key in ('filesystems','unset-environment') and old.has_option(section,key):
                value=';'.join(dict.fromkeys(x for x in (old[section][key]+';'+value).split(';') if x))+';'
            old[section][key]=value
    import io
    buf=io.StringIO();old.write(buf,space_around_delimiters=False);put(target,buf.getvalue().encode())

for source in sorted((ROOT/'home').rglob('*')):
    if not source.is_file():continue
    rel=source.relative_to(ROOT/'home');target=home/rel
    if str(rel).startswith('.local/share/flatpak/overrides/'):
        merge_ini(source,target)
    else:put(target,content(source),source.stat().st_mode&0o777)

# Both wallpapers are installed; select one in COSMIC's desktop configuration.
backgrounds=home/'.local/share/backgrounds/EVA01'
for source in sorted((ROOT/'wallpapers').glob('*.jpg')):
    put(backgrounds/source.name,source.read_bytes())
selected=backgrounds/(args.wallpaper+'.jpg')
background_template=ROOT/'home/.config/cosmic/com.system76.CosmicBackground/v1/all'
if background_template.exists():
    settings=content(background_template).decode()
    settings,count=re.subn(r'source:\s*Path\("(?:[^"\\]|\\.)*"\)',
                          lambda _: 'source: Path('+json.dumps(str(selected))+')',settings,count=1)
    if count!=1:raise SystemExit('Cannot select the wallpaper in this COSMIC background configuration.')
    put(home/'.config/cosmic/com.system76.CosmicBackground/v1/all',settings.encode())
    put(home/'.config/cosmic/com.system76.CosmicSettings.Wallpaper/v1/custom-images',
        (json.dumps([str(backgrounds/'eva01.jpg'),str(backgrounds/'purple-nebula.jpg')],indent=2)+'\n').encode())

data=home/'.local/share'
tops=['icons/Colloid-EVA01','icons/Colloid-EVA01-Dark','icons/Colloid-EVA01-Light',
      'icons/EVA01-Cursors','icons/default','themes/EVA01','color-schemes/EVA01.colors']
actions.extend('.local/share/'+p+' (assets)' for p in tops)
if not args.dry_run:
    for relative in tops:
        path=data/relative
        save(path)
        if path.is_symlink() or path.is_file():path.unlink()
        elif path.exists():shutil.rmtree(path)
    data.mkdir(parents=True,exist_ok=True)
    with tarfile.open(archive) as tar:tar.extractall(data,filter='data')

# Discover actual Zen profiles instead of restoring the original random profile ID.
zen=home/'.var/app/app.zen_browser.zen/.zen'
profiles=[]
ini=configparser.ConfigParser(interpolation=None);ini.read(zen/'profiles.ini')
for section in ini.sections():
    if section.startswith('Profile') and ini.has_option(section,'Path'):
        value=Path(ini[section]['Path'])
        profile=zen/value if ini.get(section,'IsRelative',fallback='1')=='1' else value
        if profile.resolve().is_relative_to(home.resolve()):profiles.append(profile)
profiles += [p for p in zen.glob('*') if p.is_dir() and (p/'prefs.js').exists()]
profiles=list(dict.fromkeys(profiles))
if not profiles:
    print('Zen: launch it once, quit it, then rerun this installer to apply browser chrome.')
for profile in profiles:
    for source in (ROOT/'apps/zen').glob('*'):
        relative=Path(source.name) if source.name=='user.js' else Path('chrome')/source.name
        target=profile/relative
        new=content(source).decode()
        marker=r'/\* EVA01 BEGIN \*/.*?/\* EVA01 END \*/\s*'
        managed=re.search(marker,new,re.S)
        if target.exists():
            old=re.sub(marker,'',target.read_text(),flags=re.S)
            new=old.rstrip()+'\n\n'+(managed.group() if managed else '/* EVA01 BEGIN */\n'+new+'\n/* EVA01 END */\n')
        put(target,new.encode())

for source in (ROOT/'apps/vscode').rglob('*'):
    if not source.is_file():continue
    target=home/'.config/Code/User'/source.relative_to(ROOT/'apps/vscode')
    if source.name=='settings.json':merge_json(source,target)
    else:put(target,content(source))
for source in (ROOT/'apps/vesktop').rglob('*.json'):
    merge_json(source,home/'.var/app/dev.vencord.Vesktop/config/vesktop'/source.relative_to(ROOT/'apps/vesktop'))

# Apply Obsidian appearance without importing any source-machine vault paths.
obsidian=home/'.var/app/md.obsidian.Obsidian/config/obsidian/obsidian.json'
if (ROOT/'apps/obsidian/EVA01').exists():
    vaults=json.loads(obsidian.read_text()).get('vaults',{}) if obsidian.exists() else {}
    if not vaults:print('Obsidian: open a vault once, close the app, then rerun to apply its theme.')
    for vault in vaults.values():
        cfg=Path(vault['path'])/'.obsidian'
        if not cfg.resolve().is_relative_to(home.resolve()):
            print('Obsidian: external vault skipped; copy apps/obsidian/EVA01 to its .obsidian/themes directory.');continue
        for source in (ROOT/'apps/obsidian/EVA01').rglob('*'):
            if source.is_file():put(cfg/'themes/EVA01'/source.relative_to(ROOT/'apps/obsidian/EVA01'),content(source))
        merge_json(ROOT/'apps/obsidian/appearance.json',cfg/'appearance.json')

if (ROOT/'apps/steam/EVA01').exists():
    steam=home/'.steam/steam'
    if not steam.exists():steam=home/'.local/share/Steam'
    if not steam.resolve().is_relative_to(home.resolve()):raise SystemExit('Steam root is outside this home.')
    for source in (ROOT/'apps/steam/EVA01').rglob('*'):
        if source.is_file():put(steam/'millennium/themes/EVA01'/source.relative_to(ROOT/'apps/steam/EVA01'),content(source))
    merge_json(ROOT/'apps/steam/config.json',home/'.config/millennium/config.json')
    if desktop and Path('/usr/bin/steam').exists():
        run([sys.executable,ROOT/'apps/steam/install-millennium.py'])
    else:print('Steam: user-local loader installer is available at apps/steam/install-millennium.py.')

# Install the local IntelliJ theme into matching installed IDE versions.
versions=set((home/'.config/JetBrains').glob('IntelliJIdea*'))
for version in versions:
    put(home/'.local/share/JetBrains'/version.name/'EVA01.jar',(ROOT/'assets/EVA01.jar').read_bytes())
    original=ROOT/'home/.config/JetBrains/IntelliJIdea2026.2'
    if original.exists() and version.name!=original.name:
        for source in original.rglob('*'):
            if source.is_file():put(version/source.relative_to(original),content(source))

if not args.dry_run:
    backup.mkdir(parents=True,exist_ok=True)
    (backup/'restore-manifest.json').write_text(json.dumps({'changed':actions,'saved':[str(p.relative_to(home)) for p in saved]},indent=2)+'\n')
if desktop:
    if shutil.which('systemctl') and (ROOT/'home/.config/systemd/user/eva01-legacy-theme.path').exists():
        run(['systemctl','--user','daemon-reload'])
        run(['systemctl','--user','enable','--now','eva01-legacy-theme.path'])
    for command in [('fc-cache','-f'),('gtk-update-icon-cache','-f',str(data/'icons/Colloid-EVA01-Dark'))]:
        if shutil.which(command[0]):run(command)
    if shutil.which('gsettings'):
        run(['gsettings','set','org.gnome.desktop.interface','cursor-theme','EVA01-Cursors'])
        run(['gsettings','set','org.gnome.desktop.interface','cursor-size','32'])
        run(['gsettings','set','org.gnome.desktop.interface','icon-theme','Colloid-EVA01-Dark'])
        run(['gsettings','set','org.gnome.desktop.interface','gtk-theme','EVA01'])
    if shutil.which('code'):run(['code','--install-extension',ROOT/'assets/EVA01.vsix','--force'])
    if shutil.which('xrdb') and os.environ.get('DISPLAY') and (home/'.Xresources').exists():
        run(['xrdb','-merge',home/'.Xresources'])
    if shutil.which('dbus-update-activation-environment'):
        run(['dbus-update-activation-environment','--systemd','XCURSOR_THEME=EVA01-Cursors',
             'XCURSOR_SIZE=32','XCURSOR_PATH='+str(data/'icons')+':/usr/share/icons:/usr/share/pixmaps',
             'QT_QPA_PLATFORMTHEME=qt5ct'])

print(('Would update ' if args.dry_run else 'Updated ')+str(len(actions))+' files/asset groups.')
if args.dry_run:
    print('Dry run complete; nothing changed.')
else:
    print('Previous files:',backup)
    print('Open a new terminal. Reopen themed apps; log out/in to refresh the COSMIC cursor and Qt environment.')
    print('Missing optional programs:',', '.join(x for x in ('fish','fastfetch','starship','qt5ct','qt6ct') if not shutil.which(x)) or 'none')
