#!/usr/bin/env python3
"""Check XeTeX footnotes and their actual PDF targets in both load orders."""
import os
from pathlib import Path
import subprocess
import tempfile

from pypdf import PdfReader

root = Path(__file__).resolve().parents[2]
env = os.environ.copy()
env['TEXINPUTS'] = f'.:{root}:' + env.get('TEXINPUTS', '')
with tempfile.TemporaryDirectory(prefix='bbd-xe-hyperref-') as tmp:
    work = Path(tmp)
    for order in ('before', 'after'):
        for enabled in (True, False):
            hyper = r'\usepackage[hyperfootnotes=' + str(enabled).lower() + r']{hyperref}'
            babelbidi = r'\usepackage[english]{babelbidi}'
            packages = (hyper + '\n' + babelbidi if order == 'before'
                        else babelbidi + '\n' + hyper)
            (work / 'case.tex').write_text(r'\documentclass{article}' + '\n' + packages + r'''
\begin{document}
Normal\footnote{Normal note.} RTL\RTLfootnote{RTL note.} LTR\LTRfootnote{LTR note.}
\end{document}
''')
            for _ in range(2):
                result = subprocess.run(['xelatex', '-halt-on-error', '-interaction=nonstopmode',
                                         'case.tex'], cwd=work, env=env,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                assert result.returncode == 0, result.stdout[-6000:]
            log = (work / 'case.log').read_text(errors='replace')
            assert 'Could not adapt late hyperref footnotes' not in log
            pdf = PdfReader(work / 'case.pdf')
            names = {name for name in pdf.named_destinations if name.startswith('Hfootnote.')}
            expected = {f'Hfootnote.{number}' for number in range(1, 4)} if enabled else set()
            assert names == expected, (order, enabled, names)
            annotations = pdf.pages[0].get('/Annots')
            links = set()
            if annotations:
                for reference in annotations.get_object():
                    action = reference.get_object().get('/A')
                    if action and action.get('/S') == '/GoTo':
                        links.add(str(action.get('/D')))
            assert expected <= links, (order, enabled, links)
            print(f'xelatex: hyperref {order}, hyperfootnotes={enabled}: OK')
