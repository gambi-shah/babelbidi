#!/usr/bin/env python3
"""Check pdfTeX footnote link annotations in RTL and LTR contexts."""

import os
from pathlib import Path
import subprocess
import tempfile

from pypdf import PdfReader

root = Path(__file__).resolve().parents[2]
env = os.environ.copy()
env['TEXINPUTS'] = f'{root}:' + env.get('TEXINPUTS', '')

with tempfile.TemporaryDirectory(prefix='babelbidi-pdf-links-', dir='/tmp') as temp:
    for order in ('before', 'after'):
        for links in (True, False, None):
            directory = Path(temp) / f'{order}-{links}'
            directory.mkdir()
            hyperref = (r'\usepackage' + ('' if links else '[hyperfootnotes=false]') + '{hyperref}'
                        if links is not None else '')
            babelbidi = r'\usepackage[english,farsi]{babelbidi}'
            packages = (hyperref, babelbidi) if order == 'before' else (babelbidi, hyperref)
            source = '\n'.join((
                r'\documentclass{article}',
                r'\usepackage[LAE,LFE,T1]{fontenc}',
                *packages,
                r'\begin{document}',
                r'سلام\footnote{پانویس} و\footnote{دوم}.',
                r'\selectlanguage{english}English\footnote{English note}.',
                r'\begin{minipage}{.8\linewidth}Mini\footnote{Mini note}.\end{minipage}',
                r'\end{document}',
            ))
            (directory / 'test.tex').write_text(source, encoding='utf-8')
            for _ in range(2):
                subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'test.tex'],
                               cwd=directory, env=env, check=True, stdout=subprocess.DEVNULL)
            reader = PdfReader(directory / 'test.pdf')
            annotations = [item.get_object() for page in reader.pages
                           for item in page.get('/Annots', [])]
            destinations = []
            for annotation in annotations:
                if annotation.get('/Subtype') != '/Link':
                    continue
                action = annotation.get('/A', {}).get_object()
                if action.get('/S') == '/GoTo':
                    destinations.append(str(action.get('/D')))
            if links:
                assert len(destinations) == 4, (order, destinations)
                assert len(set(destinations)) == 4, (order, destinations)
                assert set(destinations) <= set(reader.named_destinations), (order, destinations)
            else:
                assert not destinations, (order, destinations)
            print(f'{order}, hyperfootnotes={links}: OK')

    directory = Path(temp) / 'patch-failure'
    directory.mkdir()
    source = r'''\documentclass{article}
\usepackage[english]{babelbidi}
\usepackage{hyperref}
\makeatletter
\AtBeginDocument{\def\@footnotemark{\@makefnmark}}
\makeatother
\begin{document}Text\footnote{Note}.\end{document}
'''
    (directory / 'test.tex').write_text(source, encoding='utf-8')
    subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'test.tex'],
                   cwd=directory, env=env, check=True, stdout=subprocess.DEVNULL)
    assert 'Could not adapt hyperref footnote links' in (directory / 'test.log').read_text()
    print('incompatible footnote definition: warning emitted')

    directory = Path(temp) / 'texxet-disabled'
    directory.mkdir()
    source = r'''\documentclass{article}
\usepackage[english]{babelbidi}
\usepackage{hyperref}
\begin{document}\TeXXeTstate=0 Text\footnote{Note}.\end{document}
'''
    (directory / 'test.tex').write_text(source, encoding='utf-8')
    subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'test.tex'],
                   cwd=directory, env=env, check=True, stdout=subprocess.DEVNULL)
    reader = PdfReader(directory / 'test.pdf')
    assert 'Hfootnote.1' in reader.named_destinations
    annotations = reader.pages[0].get('/Annots', [])
    assert len(annotations) == 1
    action = annotations[0].get_object().get('/A', {}).get_object()
    assert action.get('/D') == 'Hfootnote.1'
    print('TeXXeT disabled: footnote link resolves')
