#!/usr/bin/env python3
"""Exercise the built-in minted Unicode display adjustment."""

import os
from collections import Counter
from pathlib import Path
import subprocess
import tempfile

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTContainer


def glyphs(item):
    if isinstance(item, LTChar):
        yield item.get_text(), item.graphicstate.ncolor, item.x0, item.y0
    elif isinstance(item, LTContainer):
        for child in item:
            yield from glyphs(child)


root = Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory(prefix='babelbidi-minted-') as directory:
    work = Path(directory)
    (work / '_minted').mkdir()
    (work / 'config').mkdir()
    (work / 'home').mkdir()
    env = dict(os.environ, HOME=str(work / 'home'),
               XDG_CONFIG_HOME=str(work / 'config'))
    env['TEXINPUTS'] = f'.:{root}:' + env.get('TEXINPUTS', '')
    for engine in ('xelatex', 'lualatex'):
        output = {}
        for enabled in (True, False):
            option = '' if enabled else ',mintedunicode=false'
            (work / 'case.tex').write_text(r'''
\documentclass{article}
\usepackage{fontspec}
\setmonofont{DejaVu Sans}
\usepackage[english''' + option + r''']{babelbidi}
\usepackage{minted}
\ExplSyntaxOn
\cs_new_eq:NN \bbd_test_word:nnn \bbd_minted_word:nnn
\cs_set_protected:Npn \bbd_minted_word:nnn #1#2#3
  {\typeout{BBD-UNICODE: \tl_to_str:n {#3}}\bbd_test_word:nnn {#1}{#2}{#3}}
\ExplSyntaxOff
\begin{document}
\begin{minted}[breaklines,breakanywhere]{latex}
\نمونه{متن فارسی}
\ڤپچژ{ABC}
\mixسلام{ABC}
\عربية{۱۲۳٤٥}
\طويلة_اسم:اختبار!123
\نیم‌فاصله{A}
\پیوند‍دار{B}
\end{minted}
\end{document}
''', encoding='utf-8')
            for attempt in range(2):
                result = subprocess.run(
                    [engine, '-shell-escape', '-interaction=nonstopmode',
                     '-halt-on-error', 'case.tex'], cwd=work, env=env,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                )
                assert result.returncode == 0, result.stdout
            log = (work / 'case.log').read_text(encoding='utf-8', errors='replace')
            assert ('BBD-UNICODE:مونه' in log) == enabled, log[-5000:]
            output[enabled] = [glyph for page in extract_pages(work / 'case.pdf')
                               for glyph in glyphs(page)]
            print(f'{engine}: mintedunicode={enabled} OK')

        for character in 'چژ':
            active = [color for char, color, _, _ in output[True] if char == character]
            inactive = [color for char, color, _, _ in output[False] if char == character]
            assert active and inactive, (engine, character)
            assert all(color == (0.0, 0.5, 0.0) for color in active), (engine, character, active)
            assert any(color != (0.0, 0.5, 0.0) for color in inactive), (engine, character, inactive)
        assert Counter(char for char, _, _, _ in output[True]) == Counter(
            char for char, _, _, _ in output[False]), f'{engine}: PDF characters changed'
        for enabled in (True, False):
            output[enabled] = [char for char, _, _, _ in sorted(
                output[enabled], key=lambda glyph: (-round(glyph[3], 0), glyph[2]))]
        if engine == 'xelatex':
            visual = ''.join(output[True])
            assert 'هنومن\\' in visual and 'ژچپڤ\\' in visual, (engine, visual)
        else:
            visual = ''.join(output[True])
            assert 'هنومن' in visual and '\\ژچپڤ' in visual, (engine, visual)
        print(f'{engine}: PDF colors and visible character preservation OK')

        images = []
        for option in ('true', 'false'):
            (work / 'case.tex').write_text(r'''
\documentclass{article}
\usepackage{fontspec}
\usepackage[english,mintedunicode=''' + option + r''']{babelbidi}
\usepackage{minted}
\begin{document}
\begin{minted}[breaklines,breakanywhere,linenos]{latex}
\textbf{Normal text}
\newcommand{\example}{Some text}
% A comment with punctuation: 12.
\end{minted}
\begin{minted}{python}
def hello():
    return "hello"
\end{minted}
\end{document}
''', encoding='utf-8')
            for attempt in range(2):
                result = subprocess.run(
                    [engine, '-shell-escape', '-interaction=nonstopmode',
                     '-halt-on-error', 'case.tex'], cwd=work, env=env,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                )
                assert result.returncode == 0, result.stdout
            raster = subprocess.run(
                ['pdftoppm', '-f', '1', '-l', '1', '-r', '100', '-png',
                 '-singlefile', 'case.pdf'], cwd=work, check=True,
                stdout=subprocess.PIPE,
            ).stdout
            images.append(raster)
        assert images[0] == images[1], f'{engine}: ASCII or Python layout changed'
        print(f'{engine}: unchanged ASCII and Python output OK')

        (work / 'sample.tex').write_text('\\نمونه{متن فارسی}\n', encoding='utf-8')
        (work / 'case.tex').write_text(r'''
\documentclass{article}
\usepackage{fontspec}
\setmonofont{DejaVu Sans}
\usepackage{minted}
\usepackage[english]{babelbidi}
\ExplSyntaxOn
\cs_new_eq:NN \bbd_test_word:nnn \bbd_minted_word:nnn
\cs_set_protected:Npn \bbd_minted_word:nnn #1#2#3
  {\typeout{BBD-UNICODE: \tl_to_str:n {#3}}\bbd_test_word:nnn {#1}{#2}{#3}}
\ExplSyntaxOff
\begin{document}
\inputminted{latex}{sample.tex}
\end{document}
''', encoding='utf-8')
        result = subprocess.run(
            [engine, '-shell-escape', '-interaction=nonstopmode',
             '-halt-on-error', 'case.tex'], cwd=work, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        assert result.returncode == 0, result.stdout
        log = (work / 'case.log').read_text(encoding='utf-8', errors='replace')
        assert 'BBD-UNICODE:مونه' in log
        print(f'{engine}: minted loaded first and inputminted OK')
