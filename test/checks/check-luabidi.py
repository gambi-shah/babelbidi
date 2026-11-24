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
from PIL import Image, ImageChops, ImageDraw

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


def check_improvements(pdfs, directory, cases):
    for page, expected, previous, regions in cases:
        for mode, text in (('babelbidi', expected), ('native', previous)):
            content = run('pdftotext', '-f', str(page), '-l', str(page),
                          '-layout', str(pdfs[mode]), '-', cwd=directory, capture=True)
            assert text in content, (page, mode, content)
        images = []
        for mode in ('native', 'babelbidi'):
            output = directory / f'{mode}-{page}-full'
            run('pdftoppm', '-f', str(page), '-l', str(page), '-r', '100',
                '-singlefile', '-png', str(pdfs[mode]), str(output), cwd=directory)
            images.append(Image.open(output.with_suffix('.png')).convert('RGB'))
        assert images[0].size == images[1].size, (page, 'page dimensions differ')
        difference = ImageChops.difference(*images)
        for left, top, right, bottom in regions:
            assert 0 <= left < right <= difference.width and 0 <= top < bottom <= difference.height
            assert difference.crop((left, top, right, bottom)).getbbox(), (page, 'region has no differences')
            ImageDraw.Draw(difference).rectangle((left, top, right - 1, bottom - 1), fill=(0, 0, 0))
        assert difference.getbbox() is None, (page, 'unexpected visual difference', difference.getbbox())


def normalized_refs(content, native):
    direction_controls = '\u061c\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069'
    content = ''.join(char for char in content if char not in direction_controls)
    if native:
        for old, new in (('dna 5etontoof LTR', 'RTL footnote 5 and'),
                         ('.eton thgiR 2', '.Right note 2'),
                         ('.enin rebmuN 9', '.Number nine 9')):
            assert content.count(old) == 1, ('unexpected native reference text', old)
            content = content.replace(old, new)
    return ' '.join(content.split())


assert normalized_refs('a\u200cb\u200dc\u200ed', False) == 'a\u200cb\u200dcd'
assert normalized_refs('a\u200cb', False) != normalized_refs('ab', False)
assert normalized_refs('a\u200db', False) != normalized_refs('ab', False)


with tempfile.TemporaryDirectory(prefix='babelbidi-luabidi-', dir='/tmp') as tmp:
    for source, variant in (('luabidi', ''), ('luabidi-options', ''), ('luabidi-options', 'wide'), ('luabidi-main', ''), ('luabidi-main', 'ltr'), ('luabidi-main', 'normal-footnote'),
                            ('luabidi-layout', 'kernel'), ('luabidi-layout', 'array'),
                            ('luabidi-refs', '')):
        outputs = {}
        pdfs = {}
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
            pdfs[mode] = pdf
            if source == 'luabidi-refs':
                content = run('pdftotext', '-layout', str(pdf), '-', cwd=directory, capture=True)
                outputs[mode] = (content, links(pdf) if PdfReader else None)
            else:
                run('pdftoppm', '-r', '100', '-png', str(pdf), 'page', cwd=directory)
                pages = sorted(directory.glob('page-*.png'))
                assert pages, (source, mode, 'no pages')
                outputs[mode] = [hashlib.sha256(page.read_bytes()).hexdigest() for page in pages]
        if PdfReader:
            boxes = [[tuple(float(value) for value in page.mediabox)
                      for page in PdfReader(str(pdfs[mode])).pages]
                     for mode in ('native', 'babelbidi')]
            assert boxes[0] == boxes[1], (source, variant, 'PDF media boxes differ', boxes)
        if source == 'luabidi-refs':
            native, actual = outputs['native'], outputs['babelbidi']
            assert 'References 1, 2, 2.' in native[0], 'native reference behavior changed'
            assert 'References 1, 2, 2.' in actual[0], 'reference numbers differ'
            assert 'RTL footnote 5 and' in actual[0], 'RTL footnote text order is incorrect'
            assert 'Right note 2' in actual[0], 'right footnote text order is incorrect'
            assert normalized_refs(native[0], True) == normalized_refs(actual[0], False), 'reference document text differs'
            if PdfReader:
                assert native[1] and native[1] == actual[1], 'link annotations differ'
            print('luabidi-refs: reference numbers and link targets match luabidi' if PdfReader
                  else 'luabidi-refs: reference numbers match; pypdf unavailable')
        else:
            native, actual = outputs['native'], outputs['babelbidi']
            assert len(native) == len(actual), (source, 'page count differs')
            different = [i for i, (a, b) in enumerate(zip(native, actual), 1) if a != b]
            cases = {
                ('luabidi', ''): ((1, 'ABC 123', '321 CBA', ((310, 200, 455, 230),)),
                                  (11, 'a_b% c', 'c %b_a', ((180, 200, 235, 223), (520, 222, 645, 240)))),
                ('luabidi-options', ''): ((1, 'Right note 1', 'eton thgiR 1', ((580, 905, 650, 930),)),),
                ('luabidi-options', 'wide'): ((1, 'Right note 1', 'eton thgiR 1', ((580, 905, 650, 930),)),),
                ('luabidi-main', ''): ((1, 'and 1', 'dna 1', ((495, 190, 530, 215),)),
                                       (2, 'ABC 123', '321 CBA', ((460, 170, 570, 200),))),
                ('luabidi-main', 'normal-footnote'): ((1, 'and 2', 'dna 2', ((490, 190, 530, 215), (560, 895, 630, 915))),
                                                      (2, 'ABC 123', '321 CBA', ((460, 170, 570, 200),))),
                ('luabidi-main', 'ltr'): ((1, 'English 123', 'English 123', ((180, 175, 355, 217),
                                                                             (195, 224, 280, 244),
                                                                             (193, 253, 265, 272),
                                                                             (195, 325, 240, 345))),
                                          (2, 'ABC 123', '321 CBA', ((180, 170, 345, 200),))),
                ('luabidi-layout', 'kernel'): ((1, 'Gamma', 'ammaG', ((510, 195, 660, 245),)),
                                                (3, 'He', 'ol', ((595, 255, 635, 300),))),
                ('luabidi-layout', 'array'): ((1, 'Gamma', 'ammaG', ((515, 195, 660, 245),)),
                                               (3, 'He', 'ol', ((595, 255, 635, 300),))),
            }.get((source, variant), ())
            assert different == [case[0] for case in cases], (source, variant, 'unexpected page differences', different)
            check_improvements(pdfs, Path(tmp), cases)
            print(f'{source} {variant}: expected direction improvements; other rendered areas match')
