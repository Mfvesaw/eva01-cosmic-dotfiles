#!/usr/bin/env python3
"""Roll back one installer run using its local backup manifest."""
from pathlib import Path
import argparse
import json
import shutil
import os

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('backup',type=Path)
parser.add_argument('--home',type=Path,default=Path.home())
args=parser.parse_args();home=args.home.absolute();backup=args.backup.absolute()
if not backup.is_relative_to(home/'.local/state/eva01/backups'):
    parser.error('Choose a backup from this home’s .local/state/eva01/backups directory.')
manifest=json.loads((backup/'restore-manifest.json').read_text())
for relative in sorted(manifest['saved'],key=lambda p:len(Path(p).parts),reverse=True):
    rel=Path(relative)
    if rel.is_absolute() or '..' in rel.parts:raise SystemExit('Unsafe manifest path')
    source=backup/rel;target=home/rel
    if target.is_symlink() or target.is_file():target.unlink()
    elif target.exists():shutil.rmtree(target)
    if source.is_symlink():target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(os.readlink(source))
    elif source.is_dir():shutil.copytree(source,target,symlinks=True)
    elif source.is_file():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
print('Previous files restored. Reopen applications or log out/in to reload them.')
