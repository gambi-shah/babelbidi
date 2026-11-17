#!/usr/bin/env python3
"""Measure Tufte note box endpoints, including material outside the page.

Requires XeLaTeX, LuaLaTeX, zref-savepos and Poppler. This is a diagnostic
regression fixture: it reports OUTSIDE/OVERLAP, rather than treating known
failures as a passing assertion. All generated files remain under /tmp.
"""
import argparse
import concurrent.futures
import csv
from itertools import product
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, help='write CSV results here')
parser.add_argument('--jobs', type=int, default=3)
parser.add_argument('--strict', action='store_true', help='fail if a BabelBidi note is outside the page or overlaps the text')
parser.add_argument('--quick', action='store_true', help='test biditufte classes only')
parser.add_argument('--fallback-only', action='store_true', help='check forced fallback and note direction only')
args = parser.parse_args()
env = os.environ.copy()
env['TEXINPUTS'] = '.:' + str(root) + ':' + str(root / 'test/checks') + ':' + env.get('TEXINPUTS', '')
fixture = root / 'test/checks/tufte-geometry.tex'

def check_fallback():
    # On the normal geometry, reverse requests the narrow left margin; with
    # reversegeometry, normal requests the narrow right margin. Both cases
    # must use the opposite margin without changing either note direction.
    template = r'''
\documentclass[oneside%s]{biditufte-handout}
\usepackage[english]{babelbidi}
\usepackage{zref-savepos}
\pagestyle{empty}
\newcommand\bounds[1]{\makebox[\marginparwidth][l]{\zsavepos{#1-left}\hfill\zsavepos{#1-right}}\par
  \noindent\zsavepos{#1-before}\hbox{A}\zsavepos{#1-after}\par}
\begin{document}
\typeout{FALLBACK-NEEDED: \the\dimexpr\marginparwidth+\marginparsep\relax}
%s
\noindent\zsavepos{text-left}\makebox[\linewidth][l]{\hfill\zsavepos{text-right}}\par
\begin{RTL}
Text\LTRmarginpar{\bounds{ltr}}\par\bigskip
\end{RTL}
\begin{LTR}
Text\RTLmarginpar{\bounds{rtl}}\par
\end{LTR}
\end{document}
'''
    for engine, mirrored in product(('xelatex', 'lualatex'), (False, True)):
        with tempfile.TemporaryDirectory(prefix='bbd-tufte-fallback-', dir='/tmp') as tmp:
            d = Path(tmp)
            (d / 'fallback.tex').write_text(template % (
                ',reversegeometry' if mirrored else '',
                r'\normalmarginpar' if mirrored else r'\reversemarginpar'))
            for _ in range(2):
                proc = subprocess.run([engine, '-interaction=nonstopmode', '-halt-on-error', 'fallback.tex'],
                                      cwd=d, env=env, stdout=subprocess.PIPE, text=True)
                if proc.returncode:
                    raise RuntimeError(f'{engine} compilation failed:\n{proc.stdout}')
            aux = (d / 'fallback.aux').read_text()
            pos = {name: int(x) / 65781.76 for name, x in re.findall(
                r'\\zref@newlabel\{([^}]+)\}\{\\posx\{(-?\d+)\}', aux)}
            info = subprocess.check_output(['pdfinfo', str(d / 'fallback.pdf')], text=True)
            width = float(re.search(r'Page size:\s+([\d.]+)', info).group(1))
            needed = float(re.search(r'FALLBACK-NEEDED:\s*([\d.]+)pt', proc.stdout).group(1)) * 72 / 72.27
            left, right = sorted((pos['text-left'], pos['text-right']))
            requested, opposite = ((width - right, left) if mirrored else (left, width - right))
            assert requested < needed <= opposite, (engine, mirrored, requested, needed, opposite)
            for note in ('ltr', 'rtl'):
                a, b = sorted((pos[note + '-left'], pos[note + '-right']))
                assert 0 <= a < b <= width, (engine, mirrored, note, a, b, width)
                assert b <= left or a >= right, (engine, mirrored, note, a, b, left, right)
                assert (b <= left) if mirrored else (a >= right), (engine, mirrored, note, a, b)
                before, after = pos[note + '-before'], pos[note + '-after']
                assert 0 <= before <= width and 0 <= after <= width, (engine, note, before, after)
                assert (before < after) if note == 'ltr' else (before > after), (engine, mirrored, note, before, after)
            print(engine, 'reversegeometry' if mirrored else 'reversemarginpar',
                  'fallback and LTR/RTL direction OK')

if args.fallback_only:
    check_fallback()
    sys.exit(0)

check_fallback()
classes = ['biditufte-handout', 'biditufte-book']
if not args.quick:
    classes += ['tufte-handout', 'tufte-book']
# The two Tufte families use different options for mirrored geometry.
options = {'biditufte': ['oneside', 'twoside', 'oneside,reversegeometry', 'oneside,narrowmargin'],
           'tufte': ['oneside', 'twoside', 'symmetric', 'oneside,narrowmargin']}
backends = [('xelatex', 'babelbidi'), ('xelatex', 'bidi'),
            ('lualatex', 'babelbidi'), ('lualatex', 'luabidi')]
case_rows = []
for policy, context, reverse, parity in product(range(4), range(3), range(2), range(2)):
    case_rows.append((len(case_rows) + 1, policy, context, reverse, parity))
# Every logical case occupies an odd and an even page.
cases = ''.join(r'\probepage{C%d}{%d}{%d}{%d}' % (i, policy, reverse, context) + '\n'
                for i, policy, context, reverse, parity in case_rows)


def run(config):
    cls, opt, engine, backend = config
    # The plain Tufte classes do not supply bidituftesidenote's directional API.
    flag = {'bidi': r'\def\NativeBidi{}', 'luabidi': r'\def\NativeLuaBidi{}'}.get(backend, '')
    class_options = opt
    if opt == 'oneside,narrowmargin':
        class_options = 'oneside'
        flag += r'\def\ProbeNarrow{}'
    if cls.startswith('tufte-') and backend == 'bidi':
        # Native Tufte sidenote fails independently with bidi on this system.
        flag += r'\def\NoTufteSide{}'
    with tempfile.TemporaryDirectory(prefix='bbd-tufte-geometry-', dir='/tmp') as tmp:
        d = Path(tmp)
        (d / 'tufte-cases.tex').write_text(cases)
        document = (r'\def\ProbeClass{' + cls + r'}\def\ProbeOptions{' + class_options + '}' + flag
                    + r'\input{' + str(fixture) + '}')
        for iteration in range(2):
            proc = subprocess.run([engine, '-interaction=nonstopmode', '-halt-on-error', document],
                                  cwd=d, env=env, text=True, stdout=subprocess.PIPE)
            if proc.returncode:
                failure = '\n'.join(line for line in proc.stdout.splitlines() if line.startswith('!'))
                return [], [(cls, opt, engine, backend, 'COMPILE_ERROR', failure)]
        aux = (d / 'tufte-geometry.aux').read_text()
        pos = {name: int(x) / 65781.76 for name, x in re.findall(
            r'\\zref@newlabel\{([^}]+)\}\{\\posx\{(-?\d+)\}', aux)}
        info = subprocess.check_output(['pdfinfo', str(d / 'tufte-geometry.pdf')], text=True)
        page_width = float(re.search(r'Page size:\s+([\d.]+)', info).group(1))
        records, errors = [], []
        expected_kinds = {'plain', 'optional'}
        if backend != 'luabidi':
            expected_kinds.update(('ltrmargin', 'rtlmargin'))
        if cls.startswith('biditufte') and backend != 'luabidi':
            expected_kinds.update(('ltrside', 'rtlside'))
        elif cls.startswith('tufte-') and backend != 'bidi':
            expected_kinds.add('side')
        for i, policy, context, reverse, parity in case_rows:
            pre = f'C{i}'
            try:
                tx0, tx1 = sorted((pos[pre + '-text-a'], pos[pre + '-text-b']))
            except KeyError as exc:
                errors.append((cls, opt, engine, backend, pre, f'missing text position {exc}'))
                continue
            kinds = ['plain', 'optional', 'ltrmargin', 'rtlmargin', 'ltrside', 'rtlside', 'side']
            for kind in kinds:
                a, b = pre + '-' + kind + '-a', pre + '-' + kind + '-b'
                if a not in pos or b not in pos:
                    if kind in expected_kinds:
                        errors.append((cls, opt, engine, backend, pre, f'missing endpoints for {kind}'))
                    continue
                x0, x1 = sorted((pos[a], pos[b]))
                outside = x0 < -0.5 or x1 > page_width + 0.5
                overlap = min(x1, tx1) - max(x0, tx0) > 0.5
                side = 'left' if x1 <= tx0 + .5 else 'right' if x0 >= tx1 - .5 else 'overlap'
                if backend == 'babelbidi' and opt == 'oneside,narrowmargin':
                    expected_side = 'left' if reverse else 'right'
                    if side != expected_side:
                        errors.append((cls, opt, engine, backend, pre, f'{kind}: expected {expected_side}, got {side}'))
                records.append(dict(cls=cls, options=opt, engine=engine, backend=backend,
                    page=i, parity='odd' if i % 2 else 'even', policy=['implicit','LTR','RTL','default'][policy],
                    context=['LTR','RTL','RTLmulti'][context], reverse=reverse, kind=kind,
                    page_width=round(page_width,2), text_left=round(tx0,2), text_right=round(tx1,2),
                    note_left=round(x0,2), note_right=round(x1,2), side=side,
                    outside=outside, overlap=overlap))
        return records, errors

configs = [(cls, opt, engine, backend) for cls in classes
           for opt in options['biditufte' if cls.startswith('biditufte') else 'tufte']
           for engine, backend in backends]
all_records, errors = [], []
with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
    for config, (records, failed) in zip(configs, pool.map(run, configs)):
        all_records.extend(records)
        errors.extend(failed)
        print(*config, 'measurements', len(records), 'outside', sum(x['outside'] for x in records),
              'overlap', sum(x['overlap'] for x in records), 'errors', len(failed), flush=True)
if args.output and all_records:
    with args.output.open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=all_records[0].keys())
        writer.writeheader()
        writer.writerows(all_records)
for error in errors:
    print('ERROR', *error)
baseline_failures = [x for x in all_records if x['backend'] == 'babelbidi'
                     and (x['outside'] or x['overlap'])]
if args.strict:
    print('BabelBidi placement failures:', len(baseline_failures))
if errors or (args.strict and baseline_failures):
    raise SystemExit(1)
