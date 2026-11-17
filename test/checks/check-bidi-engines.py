#!/usr/bin/env python3
"""Exercise bidi-specific interfaces with all three TeX engines.

Uses pdftotext for physical column positions; all output is written to /tmp.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[2]
env = os.environ.copy()
env['TEXINPUTS'] = '.:' + str(root) + ':' + env.get('TEXINPUTS', '')
source = root / 'test/checks/bidi-shared.tex'
ns = '{http://www.w3.org/1999/xhtml}'

with tempfile.TemporaryDirectory(prefix='babelbidi-engines-', dir='/tmp') as tmp:
    for engine in ('xelatex', 'lualatex', 'pdflatex'):
        directory = Path(tmp) / engine
        directory.mkdir()
        subprocess.run([engine, '-interaction=nonstopmode', '-halt-on-error', str(source)],
                       cwd=directory, env=env, check=True, stdout=subprocess.DEVNULL)
        pdf = directory / 'bidi-shared.pdf'
        bbox = subprocess.check_output(['pdftotext', '-bbox', str(pdf), '-'], text=True)
        pages = list(ET.fromstring(bbox).iter(ns + 'page'))
        assert len(pages) == 7, (engine, 'unexpected page count', len(pages))
        words = {}
        for word in pages[4].iter(ns + 'word'):
            value = ''.join(word.itertext())
            if value in ('LEFTFIRST', 'LEFTSECOND', 'RIGHTFIRST', 'RIGHTSECOND'):
                assert value not in words, (engine, 'duplicate', value)
                words[value] = float(word.attrib['xMin'])
        assert words['LEFTSECOND'] < words['RIGHTFIRST'], (engine, 'RTL columns', words)
        assert words['LEFTFIRST'] < words['RIGHTSECOND'], (engine, 'LTR columns', words)
        note_marks = {}
        for word in pages[2].iter(ns + 'word'):
            value = ''.join(word.itertext())
            if value in ('1', '2', '3', '4', '5', '6') and float(word.attrib['yMin']) > 600:
                note_marks[value] = float(word.attrib['xMin'])
        assert set(note_marks) == set('123456'), (engine, 'missing footnote marks', note_marks)
        assert max(note_marks[x] for x in '145') < min(note_marks[x] for x in '236'), (
            engine, 'footnote directions', note_marks)
        text = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
        assert '1-1' in text and '(1-1)' in text, (engine, 'section/equation separator')
        print(engine + ': bidi-specific interfaces compile; numbering and column order OK')

        for mode in ('rtl', 'ltr'):
            flags = r'\def\MainStartsLTR{}' if mode == 'ltr' else ''
            document = flags + r'\input{' + str(root / 'test/checks/main-direction.tex') + '}'
            subprocess.run([engine, '-interaction=nonstopmode', '-halt-on-error', document],
                           cwd=directory, env=env, check=True, stdout=subprocess.DEVNULL)
        print(engine + ': RTL main direction and scoped paragraph direction OK')

        for mode in ('before', 'after'):
            for caption in (False, True):
                flags = r'\def\ListingsFirst{}' if mode == 'before' else ''
                flags += r'\def\WithCaption{}' if caption else ''
                document = flags + r'\input{' + str(root / 'test/checks/listings-direction.tex') + '}'
                subprocess.run([engine, '-interaction=nonstopmode', '-halt-on-error', document],
                               cwd=directory, env=env, check=True, stdout=subprocess.DEVNULL)
        print(engine + ': listings caption direction and load order OK')
