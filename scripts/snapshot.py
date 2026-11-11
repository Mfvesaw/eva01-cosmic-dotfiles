#!/usr/bin/env python3
"""Refresh the allowlisted desktop backup; never copy entire app profiles."""
from pathlib import Path
import configparser
import base64
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
DEST = ROOT/'home'
PRIVATE = re.compile(r'password|passwd|secret|credential|access.?token|refresh.?token|api.?key|private.?key|authorization', re.I)
HISTORY = re.compile(r'^(recent(_.*)?|recentFiles|recentProjects|file_history|fileHistory|history|last_opened_files|open_files|pinned_files)$', re.I)
excluded = []

def scrub(value, trail=''):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if PRIVATE.search(key) or HISTORY.search(key):
                excluded.append(trail+'/'+key)
            else:
                result[key] = scrub(item, trail+'/'+key)
        return result
    if isinstance(value, list):
        return [scrub(item, trail) for item in value]
    return value

def write(path, content, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.replace(str(HOME), '__EVA01_HOME__'))
    path.chmod(mode)

def copy_file(source, target):
    if source.is_symlink() and not source.exists():
        excluded.append(str(source.relative_to(HOME))+' (broken symlink)'); return
    if not source.is_file(): return
    try:
        text = source.read_text()
    except UnicodeError:
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target); return
    if source.suffix == '.json':
        try: text = json.dumps(scrub(json.loads(text), str(source.relative_to(HOME))), indent=2)+'\n'
        except json.JSONDecodeError: pass
    if source.name=='user.cfg' and 'FreeCAD' in source.parts:
        tree=ET.fromstring(text)
        for parent in tree.iter():
            for child in list(parent):
                name=child.get('Name','')
                if PRIVATE.search(name) or re.search(r'MRU|RecentFiles|RecentProjects',name,re.I):
                    parent.remove(child);excluded.append('FreeCAD/'+name)
        text='<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(tree,encoding='unicode')+'\n'
    write(target, text, source.stat().st_mode & 0o777)

def include(relative):
    if relative in ('.config/environment.d/80-eva01-steam.conf', '.config/fish/functions/steam.fish'):
        return
    source = HOME/relative
    if source.is_dir():
        for p in sorted(source.rglob('*')):
            if str(p.relative_to(HOME)) in ('.config/environment.d/80-eva01-steam.conf', '.config/fish/functions/steam.fish'):
                continue
            if p.is_file() and not any(part in ('__pycache__', '.git') for part in p.parts):
                if p.suffix in ('.bak', '.log') or p.name.endswith('~'): continue
                copy_file(p, DEST/p.relative_to(HOME))
    else:
        copy_file(source, DEST/relative)

if DEST.exists(): shutil.rmtree(DEST)
for relative in [
    '.config/cosmic', '.config/fish/config.fish', '.config/fish/conf.d',
    '.config/fish/functions', '.config/fish/completions', '.config/fastfetch',
    '.config/starship.toml', '.config/gtk-3.0/settings.ini', '.config/gtk-3.0/gtk.css',
    '.config/gtk-4.0/settings.ini', '.config/gtk-4.0/gtk.css', '.config/gtk-4.0/cosmic',
    '.config/qt5ct', '.config/qt6ct', '.config/kdeglobals', '.config/kcminputrc',
    '.config/QtProject.conf', '.config/environment.d', '.config/autostart',
    '.config/systemd/user/eva01-legacy-theme.path',
    '.config/systemd/user/eva01-legacy-theme.service',
    '.config/mimeapps.list', '.config/cosmic-mimeapps.list', '.config/kicad',
    '.config/arkrc', '.config/gwenviewrc', '.config/okularrc', '.config/okularpartrc',
    '.Xresources', '.local/share/flatpak/overrides',
    '.var/app/org.freecad.FreeCAD/config/FreeCAD/v1-1/user.cfg',
    '.var/app/org.freecad.FreeCAD/data/FreeCAD/v1-1/Mod/EVA01',
    '.var/app/dev.vencord.Vesktop/config/vesktop/themes/EVA01.theme.css',
]: include(relative)

# Only application preferences; no browser history, profiles, sessions, or accounts.
apps = ROOT/'apps'
if apps.exists(): shutil.rmtree(apps)
base = HOME/'.var/app/app.zen_browser.zen/.zen'
profile = base/'wgo9rboz.Default (release)'
for name in ('userChrome.css', 'userContent.css'):
    copy_file(profile/'chrome'/name, apps/'zen'/name)
copy_file(profile/'user.js', apps/'zen/user.js')
copy_file(HOME/'.config/Code/User/settings.json', apps/'vscode/settings.json')
for folder in ('snippets', 'keybindings.json'):
    source=HOME/'.config/Code/User'/folder
    if source.is_dir():
        for p in source.rglob('*'):
            if p.is_file():copy_file(p, apps/'vscode'/p.relative_to(source.parent))
    else:copy_file(source, apps/'vscode'/folder)
for item in ('settings.json', 'settings/settings.json'):
    p = HOME/'.var/app/dev.vencord.Vesktop/config/vesktop'/item
    if p.exists():
        data = scrub(json.loads(p.read_text()), 'vesktop/'+item)
        data.pop('cloud', None)
        write(apps/'vesktop'/item, json.dumps(data, indent=2)+'\n')

# Obsidian themes/preferences only: never copy notes, attachments or workspaces.
obsidian=HOME/'.var/app/md.obsidian.Obsidian/config/obsidian/obsidian.json'
if obsidian.exists():
    for vault in json.loads(obsidian.read_text()).get('vaults',{}).values():
        cfg=Path(vault['path'])/'.obsidian'
        theme=cfg/'themes/EVA01'
        if theme.exists():
            for p in theme.rglob('*'):
                if p.is_file():copy_file(p,apps/'obsidian/EVA01'/p.relative_to(theme))
            copy_file(cfg/'appearance.json',apps/'obsidian/appearance.json')
            break
copy_file(HOME/'Downloads/EVA01/apps/obsidian/README.md',apps/'obsidian/README.md')

for version in (HOME/'.config/JetBrains').glob('IntelliJIdea*'):
    for name in ('laf.xml', 'colors.scheme.xml', 'editor-font.xml', 'console-font.xml',
                 'terminal-font.xml', 'editor.xml', 'keymap.xml', 'ui.lnf.xml'):
        include(str((version/'options'/name).relative_to(HOME)))
    for sub in ('colors', 'keymaps'):
        if (version/sub).exists(): include(str((version/sub).relative_to(HOME)))

# Runtime helpers and static assets; the old animation is intentionally excluded.
for name in ('eva01-art', 'eva01-greeting', 'eva01-sync-legacy-theme'):
    copy_file(HOME/'.local/bin'/name, DEST/'.local/bin'/name)
for p in (ROOT/'assets/ascii').iterdir():
    if p.is_file(): copy_file(p, DEST/'.local/share/eva01'/p.name)

assets = ROOT/'assets'
for source, name in [
    (HOME/'Videos/ew02clao33gf1.png', 'eva-head-source.png'),
    (HOME/'Downloads/EVA01/EVA01.ron', 'EVA01.ron'),
    (HOME/'Downloads/EVA01/palette.json', 'palette.json'),
    (HOME/'Downloads/EVA01/apps/vscode/EVA01.vsix', 'EVA01.vsix'),
    (HOME/'.local/share/JetBrains/IntelliJIdea2026.2/EVA01.jar', 'EVA01.jar'),
]:
    if source.exists(): shutil.copy2(source, assets/name)

# Bundle wallpaper and the logo-menu image, replacing session-specific portal paths.
background=DEST/'.config/cosmic/com.system76.CosmicBackground/v1/all'
if background.exists():
    text=background.read_text()
    for path in re.findall(r'__EVA01_HOME__/[^"\n]+', text):
        source=Path(path.replace('__EVA01_HOME__',str(HOME)))
        if source.is_file():
            name='wallpaper'+source.suffix
            copy_file(source, DEST/'.local/share/eva01'/name)
            old=path;new='__EVA01_HOME__/.local/share/eva01/'+name
            for cfg in [background,DEST/'.config/cosmic/com.system76.CosmicSettings.Wallpaper/v1/custom-images']:
                if cfg.exists(): cfg.write_text(cfg.read_text().replace(old,new))
logo=DEST/'.config/cosmic/dev.cappsy.CosmicExtAppletLogoMenu/v1/custom_logo_path'
if logo.exists():
    path=json.loads(logo.read_text())
    source=Path(path.replace('__EVA01_HOME__',str(HOME)))
    if not source.exists(): source=HOME/'Pictures/logo.svg'
    if source.is_file():
        # The supplied .svg is really PNG. Give the copied asset its correct suffix.
        suffix='.png' if source.read_bytes().startswith(b'\x89PNG') else source.suffix
        dest=Path('.var/app/dev.cappsy.CosmicExtAppletLogoMenu/data/eva01')/('logo'+suffix)
        copy_file(source, DEST/dest)
        logo.write_text(json.dumps('__EVA01_HOME__/'+str(dest))+'\n')

metadata=ROOT/'metadata'; metadata.mkdir(exist_ok=True)
def record(name, command):
    try:
        result=subprocess.run(command,capture_output=True,text=True,check=True)
        (metadata/name).write_text(result.stdout)
    except (FileNotFoundError,subprocess.CalledProcessError): pass
record('rpm-packages.txt',['rpm','-qa','--qf','%{NAME}\n'])
record('flatpak-apps.tsv',['flatpak','list','--app','--columns=application,origin,branch'])
record('flatpak-remotes.tsv',['flatpak','remotes','--user','--columns=name,url'])
record('vscode-extensions.txt',['code','--list-extensions'])
record('font.txt',['fc-match','Nimbus Mono PS','--format','%{family}\n%{file}\n'])

# These are public repository-signing keys, not user authentication keys.
remote_config=configparser.ConfigParser(interpolation=None)
remote_config.read(HOME/'.local/share/flatpak/repo/config')
for section in remote_config.sections():
    if not section.startswith('remote "'): continue
    name=section.split('"')[1]
    if not re.fullmatch(r'[a-zA-Z0-9_.-]+',name):continue
    values=remote_config[section];url=values.get('url','')
    if not url.startswith('https://') or '@' in url:continue
    keyring=HOME/'.local/share/flatpak/repo'/(name+'.trustedkeys.gpg')
    if not keyring.exists():continue
    definition=configparser.ConfigParser(interpolation=None);definition.optionxform=str
    definition['Flatpak Repo']={'Title':values.get('xa.title',name),'Url':url,
                               'GPGKey':base64.b64encode(keyring.read_bytes()).decode()}
    import io
    buf=io.StringIO();definition.write(buf,space_around_delimiters=False)
    write(metadata/'remotes'/(name+'.flatpakrepo'),buf.getvalue())

# Keep assets as one archive rather than tens of thousands of icon Git objects.
archive=assets/'desktop-assets.tar.xz'
if not archive.exists() or os.environ.get('EVA01_REFRESH_ASSETS')=='1':
    paths=['icons/Colloid-EVA01','icons/Colloid-EVA01-Dark','icons/Colloid-EVA01-Light',
           'icons/EVA01-Cursors','icons/default','themes/EVA01','color-schemes/EVA01.colors']
    subprocess.run(['tar','--sort=name','--owner=0','--group=0','--numeric-owner','-cJf',str(archive),
                    '-C',str(HOME/'.local/share')]+paths,check=True)

report={'created':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'excluded_fields':excluded,'source_home':'__EVA01_HOME__',
        'scope':'COSMIC and allowlisted application preferences; account data and histories excluded'}
(metadata/'snapshot.json').write_text(json.dumps(report,indent=2)+'\n')
print('Snapshot refreshed. Run scripts/check-backup.py before committing.')
