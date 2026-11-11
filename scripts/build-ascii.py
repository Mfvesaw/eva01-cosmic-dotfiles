#!/usr/bin/env python3
"""Convert the supplied EVA head into colored, ordinary ASCII terminal cells.

Pillow is needed to rebuild the assets, but not to display them.
"""
from pathlib import Path
import argparse
import json
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('image', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
im = Image.open(args.image).convert('RGB')
mask = im.point(lambda value: 255 if value > 25 else 0).convert('L')
im = im.crop(mask.getbbox())
# Preserve the source's violet armor, blue jaw, amber neck and lime details.
palette = ['#915ADA', '#602EB3', '#A071DF', '#7B89EC', '#98A4F8',
           '#99E550', '#DF9326', '#C67F19', '#342541']
rgb = [tuple(bytes.fromhex(c[1:])) for c in palette]
variants = {}
for width in (28, 36, 48, 64):
    height = round(im.height / im.width * width * 0.48)
    small = im.resize((width, height), Image.Resampling.BOX)
    lines, roles = [], []
    for y in range(height):
        line, row = '', ''
        for x in range(width):
            pixel = small.getpixel((x, y))
            level = max(pixel)
            if level < 30:
                line += ' '; row += '0'
            else:
                index = min(range(len(rgb)), key=lambda i: sum((a-b)**2 for a, b in zip(pixel, rgb[i])))
                # ASCII only; no blocks, Braille or terminal image protocol.
                line += ':' if level < 80 else '+' if level < 130 else '#' if level < 200 else '@'
                row += str(index + 1)
        lines.append(line.rstrip()); roles.append(row[:len(lines[-1])])
    variants[str(width)] = dict(lines=lines, roles=roles)
args.output.mkdir(parents=True, exist_ok=True)
(args.output/'eva-head.json').write_text(json.dumps(dict(palette=palette, variants=variants), indent=2)+'\n')
for width, variant in variants.items():
    (args.output/f'eva-head-{width}.txt').write_text('\n'.join(variant['lines'])+'\n')
variant = variants['36']
colored = []
for line, roles in zip(variant['lines'], variant['roles']):
    previous = None; output = ''
    for char, role in zip(line, roles):
        if char != ' ' and role != previous:
            output += '$'+role; previous = role
        output += char
    colored.append(output)
(args.output/'eva-head-fastfetch.txt').write_text('\n'.join(colored)+'\n')
