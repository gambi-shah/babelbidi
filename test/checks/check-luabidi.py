#!/usr/bin/env python3
"""Compare shared LuaLaTeX interfaces with the installed luabidi.

Requires LuaLaTeX, Amiri, DejaVu Sans, and Poppler. Uses only /tmp for output.
The reference case also compares actual PDF annotations when pypdf is installed.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

root = Path(__file__).resolve().parents[2]
env = os.environ.copy()
env['TEXINPUTS'] = '.:' + str(root) + ':' + env.get('TEXINPUTS', '')


def run(*args, cwd, capture=False):
    return subprocess.run(args, cwd=cwd, env=env, check=True,
                          stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
                          text=True).stdout


def resolve(obj):
    return obj.get_object() if hasattr(obj, "get_object") else obj


def links(pdf):
    result = []
    for page in PdfReader(str(pdf)).pages:
        annotations = resolve(page.get('/Annots', []))
        for item in annotations:
            annotation = resolve(item)
            action = resolve(annotation.get('/A', {}))
            if annotation.get('/Subtype') == '/Link' and action.get('/S') == '/GoTo':
                destination = resolve(action.get('/D'))
                rect = resolve(annotation['/Rect'])
                result.append((str(destination),
                               tuple(round(float(x), 3) for x in rect)))
    return sorted(result)


with tempfile.TemporaryDirectory(prefix='babelbidi-luabidi-', dir='/tmp') as tmp:
    for source, variant in (('luabidi', ''), ('luabidi-options', ''), ('luabidi-options', 'wide'), ('luabidi-main', ''), ('luabidi-main', 'ltr'), ('luabidi-main', 'normal-footnote'),
                            ('luabidi-layout', 'kernel'), ('luabidi-layout', 'array'),
                            ('luabidi-refs', '')):
        outputs = {}
        for mode in ('native', 'babelbidi'):
            directory = Path(tmp) / (source + '-' + variant + '-' + mode)
            directory.mkdir()
            flag = r'\def\UseNativeLuaBidi{}' if mode == 'native' else ''
            if variant == 'normal-footnote':
                flag += r'\def\MainNormalFootnote{}'
            if variant == 'wide':
                flag += r'\def\UseWideRule{}'
            if variant == 'ltr':
                flag += r'\def\MainStartsLTR{}'
            if variant == 'array':
                flag += r'\def\UseArray{}'
            document = flag + r'\input{' + str(root / 'test/checks' / (source + '.tex')) + '}'
            for _ in range(2):
                run('lualatex', '-interaction=nonstopmode', '-halt-on-error', document, cwd=directory)
            pdf = directory / (source + '.pdf')
            if source == 'luabidi-refs':
                content = run('pdftotext', '-layout', str(pdf), '-', cwd=directory, capture=True)
                outputs[mode] = (content, links(pdf) if PdfReader else None)
            else:
                run('pdftoppm', '-r', '100', '-png', str(pdf), 'page', cwd=directory)
                pages = sorted(directory.glob('page-*.png'))
                assert pages, (source, mode, 'no pages')
                outputs[mode] = [hashlib.sha256(page.read_bytes()).hexdigest() for page in pages]
        if source == 'luabidi-refs':
            native, actual = outputs['native'], outputs['babelbidi']
            assert 'References 1, 2, 2.' in native[0], 'native reference behavior changed'
            assert native[0] == actual[0], 'footnote reference text differs'
            if PdfReader:
                assert native[1] and native[1] == actual[1], 'link annotations differ'
            print('luabidi-refs: text and link targets match luabidi' if PdfReader
                  else 'luabidi-refs: text matches; pypdf unavailable')
        else:
            native, actual = outputs['native'], outputs['babelbidi']
            assert len(native) == len(actual), (source, 'page count differs')
            different = [i for i, (a, b) in enumerate(zip(native, actual), 1) if a != b]
            assert not different, (source, 'rendered pages differ', different)
            print(f'{source} {variant}: {len(native)} rendered pages match luabidi')
