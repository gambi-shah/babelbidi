#!/usr/bin/env python3
"""Check physical digit order inside directional text and TikZ nodes."""

import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTContainer

root = Path(__file__).resolve().parents[2]
source = root / 'test/checks/inline-digits.tex'
env = os.environ.copy()
env['TEXINPUTS'] = f'{root}:' + env.get('TEXINPUTS', '')
namespace = {'html': 'http://www.w3.org/1999/xhtml'}


def glyphs(container):
    for item in container:
        if isinstance(item, LTChar):
            yield item
        elif isinstance(item, LTContainer):
            yield from glyphs(item)


with tempfile.TemporaryDirectory(prefix='babelbidi-inline-', dir='/tmp') as temp:
    for engine in ('xelatex', 'lualatex'):
        directory = Path(temp) / engine
        directory.mkdir()
        subprocess.run([engine, '-interaction=nonstopmode', '-halt-on-error',
                        str(source)], cwd=directory, env=env, check=True,
                       stdout=subprocess.DEVNULL)
        xml = subprocess.check_output(
            ['pdftotext', '-bbox-layout', str(directory / 'inline-digits.pdf'), '-'],
            cwd=directory)
        document = ET.fromstring(xml)
        words = document.findall('.//html:word', namespace)
        texts = [word.text or '' for word in words]
        digit_lines = {}
        mixed_lines = {}
        for page in extract_pages(str(directory / 'inline-digits.pdf')):
            for glyph in glyphs(page):
                if glyph.get_text() in '۱۲۳۴':
                    key = round(glyph.y0, 1)
                    digit_lines.setdefault(key, []).append((glyph.x0, glyph.get_text()))
                if glyph.get_text() in 'ABC5678':
                    key = round(glyph.y0, 1)
                    mixed_lines.setdefault(key, []).append((glyph.x0, glyph.get_text()))
        assert len(digit_lines) == 7, (engine, digit_lines)
        for baseline, line in digit_lines.items():
            assert ''.join(char for _, char in sorted(line)) == '۱۲۳۴', (engine, baseline, line)
        mixed = [''.join(char for _, char in sorted(line)) for line in mixed_lines.values()]
        expected = '5678ABC' if engine == 'xelatex' else 'ABC5678'
        assert expected in mixed, (engine, mixed)
        assert 'a_b%' in texts, (engine, texts)
        print(f'{engine}: inline and paragraph digits, nested directions OK')
