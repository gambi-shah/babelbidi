#!/usr/bin/env python3
"""Create a CTAN archive from package files and the published manuals.

Usage: python3 tools/make-ctan.py /tmp/babelbidi-ctan.zip
Tests, generated test PDFs and temporary reports are intentionally excluded.
"""
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path, help='destination ZIP file')
args = parser.parse_args()
files = [root / name for name in ('README.md', 'LICENSE', 'THIRD-PARTY-NOTICES.md')]
for pattern in ('*.sty', '*.def', '*.lua', '*.cwl'):
    files.extend(sorted(root.glob(pattern)))
for name in ('babelbidi.tex', 'babelbidi.pdf', 'amikhteh-logo.tex', 'amikhteh-logo.pdf'):
    files.append(root / 'doc' / name)
missing = [str(p) for p in files if not p.is_file()]
if missing:
    parser.error('missing release files: ' + ', '.join(missing))
with ZipFile(args.output, 'w', ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path, Path('babelbidi') / path.relative_to(root))
print(f'Wrote {args.output} ({len(files)} files)')
