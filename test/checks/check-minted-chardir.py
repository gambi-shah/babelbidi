#!/usr/bin/env python3
"""Check minted character properties and unsupported-engine errors."""
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
env = os.environ.copy()
env["TEXINPUTS"] = ".:" + str(root) + ":" + env.get("TEXINPUTS", "")

with tempfile.TemporaryDirectory(prefix="babelbidi-chardir-", dir="/tmp") as tmp:
    directory = Path(tmp)
    (directory / "_minted").mkdir()
    (directory / "test.aux").touch()
    (directory / "code.txt").write_text(
        "first.\n|\\checkdir{inside-input}|second.\n", encoding="utf-8")
    (directory / "test.tex").write_text(r"""\documentclass{article}
\usepackage[english]{babelbidi}
\usepackage{minted}
\babelcharproperty{`.}{direction}{al}
\def\checkdir#1{\directlua{texio.write_nl('term and log',
  'DIRSTATE #1: '..tostring(Babel.characters[46].d))}}
\begin{document}
\checkdir{before}
\begin{minted}[escapeinside=||,chardir={{.}{l}}]{text}
|\checkdir{inside-environment}|first.
\end{minted}
\checkdir{environment}
\inputminted[escapeinside=||,chardir={{.}{en}}]{text}{code.txt}
\checkdir{input}
\begin{minted}[chardir={{.}{r}}]{text}
second.
\end{minted}
\checkdir{after}
Ordinary text. \mintinline{text}{ordinary.}
\end{document}
""", encoding="utf-8")
    for _ in range(2):
        result = subprocess.run(["lualatex", "-shell-escape", "-interaction=nonstopmode",
                                 "-halt-on-error", "test.tex"], cwd=directory, env=env,
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode == 0, result.stdout
    for label in ("before", "environment", "input", "after"):
        assert "DIRSTATE " + label + ": al" in result.stdout, result.stdout
    assert "DIRSTATE inside-environment: l" in result.stdout, result.stdout
    assert "DIRSTATE inside-input: en" in result.stdout, result.stdout

    inline = r"""\documentclass{article}
\usepackage[english]{babelbidi}
\usepackage{minted}
\begin{document}
Ordinary text \mintinline[chardir={{.}{r}}]{text}{example.}
\end{document}
"""
    (directory / "inline.tex").write_text(inline, encoding="utf-8")
    for engine in ("lualatex", "xelatex", "pdflatex"):
        result = subprocess.run([engine, "-shell-escape", "-interaction=nonstopmode",
                                 "-halt-on-error", "inline.tex"], cwd=directory, env=env,
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode != 0, (engine, result.stdout)
        expected = ("vertical mode (preamble or between paragraphs)" if engine == "lualatex"
                    else "The minted chardir option requires LuaTeX")
        assert expected in result.stdout, (engine, result.stdout)
    print("minted environment and input restore prior direction; inline and engine limits verified")
