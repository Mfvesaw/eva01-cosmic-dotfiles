#!/usr/bin/env python3
"""Check backup scope, common credential formats, archive paths and checksums."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import tarfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--write-checksums',action='store_true')
args=parser.parse_args()
patterns=[
    re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{20,}'),
    re.compile(r'\bgithub_pat_[A-Za-z0-9_]{30,}'),
    re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
    re.compile(r'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}'),
    re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{20,}'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    re.compile(r'https?://[^/\s:@]+:[^/\s@]+@'),
]
forbidden={'cookies.sqlite','logins.json','key4.db','places.sqlite','fish_history',
           'hosts.yml','.env','credentials','Login Data','Cookies','user-tokens.json'}
errors=[];files=[]
for p in sorted(ROOT.rglob('*')):
    rel=p.relative_to(ROOT)
    if '.git' in rel.parts or '__pycache__' in rel.parts or not p.is_file():continue
    if p.name in forbidden or any(x in rel.parts for x in ('sessionData','workspaceStorage','globalStorage')):
        errors.append('Forbidden account/history path: '+str(rel))
    if p.stat().st_size>=95*1024*1024:errors.append('Too large for ordinary GitHub Git: '+str(rel))
    if p.name=='SHA256SUMS':continue
    files.append(p)
    try:text=p.read_text()
    except UnicodeError:continue
    for pattern in patterns:
        if pattern.search(text):errors.append('Potential credential in '+str(rel))
    if str(rel).startswith(('home/','apps/')) and '/home/aykd' in text:
        errors.append('Nonportable home path in '+str(rel))
    if p.name=='userContent.css' and ('https?://' in text or '@-moz-document domain(' in text):
        errors.append('Website styling should be disabled: '+str(rel))
with tarfile.open(ROOT/'assets/desktop-assets.tar.xz') as tar:
    members=tar.getmembers()
    for member in members:
        rel=PurePosixPath(member.name)
        if rel.is_absolute() or '..' in rel.parts or rel.parts[0] not in ('icons','themes','color-schemes'):
            errors.append('Unsafe archive path: '+member.name)
        try:tarfile.data_filter(member,'/tmp/eva01-asset-validation')
        except tarfile.FilterError:errors.append('Unsafe archive entry: '+member.name)
if errors:
    raise SystemExit('\n'.join(sorted(set(errors))))
manifest=ROOT/'metadata/SHA256SUMS'
if args.write_checksums:
    manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT))+'\n' for p in files))
elif manifest.exists():
    for line in manifest.read_text().splitlines():
        expected,relative=line.split('  ',1)
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()!=expected:
            raise SystemExit('Checksum mismatch: '+relative)
print(f'Checked {len(files)} files and {len(members)} icon/theme archive entries; no common credential patterns found.')
