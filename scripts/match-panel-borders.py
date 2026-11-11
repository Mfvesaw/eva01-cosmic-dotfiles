#!/usr/bin/env python3
"""Match COSMIC's panel borders to the active dark theme's window hint.
Run again after importing/rebuilding a theme; COSMIC regenerates divider colors.
"""
from pathlib import Path
import datetime, json, re, shutil
root = Path.home()/'.config/cosmic'
theme = root/'com.system76.CosmicTheme.Dark/v2'
hint = (theme/'window_hint').read_text()
hex_match = re.search(r'#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?', hint)
if hex_match:
    color = hex_match.group()[:7].upper()+'FF'
else:
    rgb = [float(re.search(r'\b'+channel+r':\s*([\d.eE+-]+)',hint).group(1)) for channel in ('red','green','blue')]
    color = '#'+''.join(f'{round(v*255):02X}' for v in rgb)+'FF'
width = 1.0  # Keep the requested thin panel/dock outlines.
background = theme/'background'
old = background.read_text()
new, count = re.subn(r'(?m)^(    divider:\s*)[^\n]+',lambda m: m.group(1)+'"'+color+'",',old)
if count != 1:
    raise SystemExit('Expected one top-level background divider; no settings changed.')
changes = {background:new}
for name in ('Panel','Dock'):
    panel = root/f'com.system76.CosmicPanel.{name}/v1'
    changes[panel/'border_width'] = f'{width:.1f}\n'
    changes[panel/'keep_style_on_maximize'] = 'true\n'
backup = Path.home()/'Downloads/EVA01/backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
backup.mkdir(parents=True)
manifest = []
for path, content in changes.items():
    relative = path.relative_to(root)
    saved = backup/relative
    exists = path.exists()
    if exists:
        saved.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,saved)
    manifest.append({'path':str(path),'backup':str(saved) if exists else None})
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for path,content in changes.items():
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content)
print(f'Panel and Dock borders: {color}, {width:g} px; preserved when maximized.')
print(f'Backup: {backup}')
