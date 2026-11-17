#!/usr/bin/env python3
"""Check listing code direction and caption state across engines/load orders."""
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
env = os.environ.copy()
env['TEXINPUTS'] = '.:' + str(root) + ':' + env.get('TEXINPUTS', '')
source = root / 'test/checks/listings-direction.tex'
with tempfile.TemporaryDirectory(prefix='babelbidi-listings-', dir='/tmp') as tmp:
    for engine in ('xelatex', 'lualatex', 'pdflatex'):
        for variant, flags in (('default', ''), ('first', r'\def\ListingsFirst{}'),
                               ('caption', r'\def\WithCaption{}'),
                               ('first-caption', r'\def\ListingsFirst{}\def\WithCaption{}')):
            directory = Path(tmp) / (engine + '-' + variant)
            directory.mkdir()
            document = flags + r'\input{' + str(source) + '}'
            result = subprocess.run([engine, '-interaction=nonstopmode', '-halt-on-error', document],
                                    cwd=directory, env=env, stdout=subprocess.PIPE, text=True)
            if result.returncode:
                raise RuntimeError(f'{engine} {variant} compilation failed:\n{result.stdout[-3000:]}')
            content = subprocess.check_output(['pdftotext', '-layout',
                                               str(directory / 'listings-direction.pdf'), '-'], text=True)
            assert any('int fourth' in line for line in content.splitlines()), (
                engine, variant, 'RTL-context code is not displayed in LTR order', content)
            assert 'htruof' not in content, (engine, variant, 'reversed code', content)
            print(f'{engine} {variant}: caption state and RTL-context code order OK')
