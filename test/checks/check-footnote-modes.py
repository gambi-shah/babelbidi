#!/usr/bin/env python3
"""Check rule selectors and normal/paragraph transitions on non-XeTeX engines."""
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
env = os.environ.copy()
env["TEXINPUTS"] = ".:" + str(root) + ":" + env.get("TEXINPUTS", "")
source = r"""\documentclass{article}
\usepackage[extrafootnotefeatures,english]{babelbidi}
\makeatletter
\let\savedrule\footnoterule
\def\checkrule#1{\autofootnoterule\leftfootnoterule\LRfootnoterule
  \rightfootnoterule\RLfootnoterule\textwidthfootnoterule
  \ifx\savedrule\footnoterule\else\errmessage{Rule changed #1}\fi
  \typeout{RULE-#1-MODE-\bbd@extra@mode}}
\makeatother
\begin{document}
\checkrule{normal}Normal\footnote{FIRSTNOTE}.
\clearpage\paragraphfootnotes\checkrule{paragraph}
Paragraph\footnote{SECONDNOTE}.\clearpage\normalfootnotes
\checkrule{restored}Normal again\footnote{THIRDNOTE}.
\end{document}
"""
with tempfile.TemporaryDirectory(prefix="babelbidi-footnote-modes-", dir="/tmp") as tmp:
    path = Path(tmp) / "test.tex"
    path.write_text(source, encoding="utf-8")
    for engine in ("lualatex", "pdflatex"):
        result = subprocess.run([engine, "-interaction=nonstopmode", "-halt-on-error",
                                 "test.tex"], cwd=tmp, env=env, text=True,
                                stdout=subprocess.PIPE)
        assert result.returncode == 0, (engine, result.stdout)
        for marker in ("RULE-normal-MODE-1", "RULE-paragraph-MODE-0",
                       "RULE-restored-MODE-1"):
            assert marker in result.stdout, (engine, marker)
        output = subprocess.check_output(["pdftotext", str(Path(tmp) / "test.pdf"), "-"],
                                         text=True)
        for word in ("FIRSTNOTE", "SECONDNOTE", "THIRDNOTE"):
            assert word in output, (engine, word, output)
        print(engine, "normal/paragraph transitions and persistent rule policy OK")
