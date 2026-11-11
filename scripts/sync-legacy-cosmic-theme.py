#!/usr/bin/env python3
"""Keep COSMIC v1 clients in sync with the active v2 dark theme.

Older applets serialize palette colors as RGBA tuples, not v2 hex strings.
The field list is from the libcosmic revision used by cosmic-pomodoro 0.1.0.
"""
from pathlib import Path
import argparse
import datetime
import json
import re
import shutil

FIELDS = '''name background primary secondary accent success destructive warning
accent_button success_button destructive_button warning_button icon_button
link_button text_button button palette spacing corner_radii is_dark
is_high_contrast gaps active_hint window_hint is_frosted shade accent_text
control_tint text_tint'''.split()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--home', type=Path, default=Path.home())
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args()
home = args.home.expanduser().absolute()
root = home/'.config/cosmic/com.system76.CosmicTheme.Dark'
source, target = root/'v2', root/'v1'
if not source.is_dir():
    raise SystemExit('No COSMIC v2 dark theme found.')

def color(match, rgb_only=False):
    value=match.group(1)
    if len(value)==6:value+='FF'
    channels=['red','green','blue'] if rgb_only else ['red','green','blue','alpha']
    return '('+', '.join(name+': '+repr(int(value[2*i:2*i+2],16)/255.0)
                         for i,name in enumerate(channels))+')'

changes={}
for key in FIELDS:
    path=source/key
    if key=='is_frosted' and not path.exists():
        frosted=source/'frosted'
        value='true\n' if frosted.exists() and frosted.read_text().strip() not in ('None','Off','Disabled') else 'false\n'
    elif path.exists():
        value=re.sub(r'"#([0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?)"',
                     lambda m:color(m,key in ('control_tint','text_tint')),path.read_text())
    else:
        continue
    dest=target/key
    if not dest.exists() or dest.read_text()!=value:changes[dest]=value
if args.dry_run:
    print(f'Would update {len(changes)} legacy COSMIC theme fields.');raise SystemExit(0)
if not changes:
    print('Legacy COSMIC theme already matches EVA01.');raise SystemExit(0)
backup=home/'.local/state/eva01/legacy-theme-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
backup.mkdir(parents=True)
manifest=[]
for path,value in changes.items():
    relative=path.relative_to(home)
    if path.exists():
        saved=backup/relative;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,saved)
    manifest.append({'path':str(relative),'existed':path.exists()})
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
target.mkdir(parents=True,exist_ok=True)
for path,value in changes.items():
    temp=path.with_name(path.name+'.eva01-tmp');temp.write_text(value);temp.replace(path)
print(f'Updated {len(changes)} legacy COSMIC theme fields. Backup: {backup}')
